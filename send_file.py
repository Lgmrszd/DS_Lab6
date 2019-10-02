import socket
import argparse
import os
import common


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    file_path = args.file_path
    filename = os.path.basename(file_path)
    s = socket.socket()
    s.connect((args.host, args.port))

    fd = open(file_path, "rb")
    file_size = os.path.getsize(file_path)
    init_packet = common.InitPacket(filename, file_size)
    out_packet_bytes = init_packet.serialize()
    s.sendall(out_packet_bytes)

    in_packet_bytes = s.recv(1024)
    in_packet = common.MyPacket.deserialize(in_packet_bytes)
    print(f"Code {in_packet.get_code()}, message: {in_packet.message}")
    bytes_read = fd.read(4096)
    bytes_sent = 0
    while bytes_read:
        bytes_sent += len(bytes_read)
        s.sendall(bytes_read)

        in_packet_bytes = s.recv(1024)
        in_packet = common.MyPacket.deserialize(in_packet_bytes)
        print(f"Code {in_packet.get_code()}, message: {in_packet.message}")

        print(f"Sent {len(bytes_read)} bytes, "
              f"total {bytes_sent}/{file_size} "
              f"({(bytes_sent / file_size):.2%})")

        bytes_read = fd.read(4096)

    close_packet = common.CloserPacket()
    close_packet_bytes = close_packet.serialize()
    s.sendall(close_packet_bytes)
    s.shutdown(socket.SHUT_WR)

    in_packet_bytes = s.recv(1024)
    in_packet = common.MyPacket.deserialize(in_packet_bytes)
    print(f"Code {in_packet.get_code()}, message: {in_packet.message}")
    s.close()


if __name__ == "__main__":
    main()
