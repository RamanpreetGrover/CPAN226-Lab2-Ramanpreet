import socket
import argparse
import struct  # IMPROVEMENT: used to unpack sequence numbers from packets


def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    print(f"[*] Reliable server listening on port {port}")

    try:
        while True:
            expected_seq = 0  # IMPROVEMENT: next expected sequence number
            buffer = {}       # IMPROVEMENT: buffer for out-of-order packets
            f = None

            while True:
                data, addr = sock.recvfrom(4096 + 4)

                seq_num = struct.unpack('!I', data[:4])[0]  # IMPROVEMENT: extract sequence number
                payload = data[4:]                           # IMPROVEMENT: extract payload

                # Send ACK immediately
                ack_packet = struct.pack('!I', seq_num)     # IMPROVEMENT: build ACK
                sock.sendto(ack_packet, addr)                # IMPROVEMENT: send ACK

                # EOF packet
                if len(payload) == 0:
                    print("[*] End of file received.")
                    break

                if f is None:
                    ip, sender_port = addr
                    filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(filename, 'wb')
                    print(f"[*] Receiving file from {addr} as '{filename}'")

                if seq_num == expected_seq:
                    f.write(payload)  # IMPROVEMENT: write in-order packet
                    expected_seq += 1

                    while expected_seq in buffer:
                        f.write(buffer.pop(expected_seq))  # IMPROVEMENT: write buffered packets
                        expected_seq += 1

                elif seq_num > expected_seq:
                    buffer[seq_num] = payload  # IMPROVEMENT: buffer out-of-order packet

                else:
                    pass  # IMPROVEMENT: ignore duplicate packet

            if f:
                f.close()
                print("[*] File reception complete.")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    finally:
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001)
    parser.add_argument("--output", type=str, default="received_file.jpg")
    args = parser.parse_args()

    run_server(args.port, args.output)
