import socket
import argparse
import time
import os
import struct  # IMPROVEMENT: used to pack sequence numbers into packets


def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)  # IMPROVEMENT: timeout for ACK reception
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        seq_num = 0  # IMPROVEMENT: initialize sequence number

        with open(input_file, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break

                packet = struct.pack('!I', seq_num) + chunk  # IMPROVEMENT: add sequence number

                # Stop-and-wait: resend until ACK received
                while True:
                    sock.sendto(packet, server_address)  # IMPROVEMENT: send packet
                    try:
                        ack, _ = sock.recvfrom(4)  # IMPROVEMENT: wait for ACK
                        ack_seq = struct.unpack('!I', ack)[0]

                        if ack_seq == seq_num:
                            break  # IMPROVEMENT: correct ACK received
                    except socket.timeout:
                        continue  # IMPROVEMENT: retransmit on timeout

                seq_num += 1  # IMPROVEMENT: move to next packet

        # Send EOF packet
        eof_packet = struct.pack('!I', seq_num)  # IMPROVEMENT: EOF packet
        sock.sendto(eof_packet, server_address)
        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1")
    parser.add_argument("--target_port", type=int, default=12001)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)
