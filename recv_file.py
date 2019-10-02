import socket
import os
import sys
import argparse
from threading import Thread
import common


def guess_filename(path, filename):
    new_filename = os.path.join(path, filename)
    num = 1
    while os.path.exists(new_filename):
        suffix = f"_copy{num}"
        name, extension = os.path.splitext(filename)
        new_filename = os.path.join(path, name+suffix+extension)
        num += 1
    return new_filename

#
# class FileSaver:
#     def __init__(self, filename):


class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket, path: str):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        self.path = path
        self.__file_size = 0
        self.__bytes_received = 0
        # In case if write happens and file is closed
        self.__fd = open(os.devnull, "wb")

    def init_file(self, filename):
        # Allocate space for file
        with open(filename, "xb") as fd:
            fd.seek(self.__file_size-1)
            fd.write(b"\0")
            fd.close()
        # Open for writing
        self.__fd = open(filename, "rb+")

    def write_file(self, data: bytes):
        self.__bytes_received += len(data)
        self.__fd.write(data)

    def close_file(self):
        self.__fd.close()
        # In case if write happens and file is closed
        self.__fd = open(os.devnull, "wb")

    def run(self):
        while True:
            data = self.sock.recv(1024)
            if data:
                packet = common.MyPacket.deserialize(data)
                packet_code = packet.get_code()
                if packet_code == common.CODE_INIT:
                    filename = guess_filename(self.path, packet.filename)
                    self.__file_size = packet.filesize
                    self.init_file(filename)
                    print(f"{self.name}: File size {self.__file_size}")
                    print(f"{self.name}: Saving as {filename}")
                    packet_bytes = common.ResponsePacket(common.CODE_INIT_OK, f"Saving as {filename}").serialize()
                    self.sock.sendall(packet_bytes)
                elif packet_code == common.CODE_DATA:
                    self.write_file(packet.data)
                    print(f"{self.name}: Got {len(packet.data)} bytes, "
                          f"total {self.__bytes_received}/{self.__file_size} "
                          f"({(self.__bytes_received/self.__file_size):.2%})")
                    packet_bytes = common.ResponsePacket(common.CODE_DATA_OK, f"Success").serialize()
                    self.sock.sendall(packet_bytes)
                elif packet_code == common.CODE_END:
                    self.close_file()
                    self.sock.shutdown(socket.SHUT_RD)
                    packet_bytes = common.ResponsePacket(common.CODE_END_OK, f"File received").serialize()
                    self.sock.sendall(packet_bytes)
                    self.sock.close()
                    print(self.name + ' disconnected')
                    return
            else:
                self.close_file()
                self.sock.close()
                print(self.name + ' disconnected')
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="./")
    parser.add_argument("--port", type=int, default=8800)
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Path {args.path} is invalid")
        return 1

    print(f"Save path is {args.path}")
    client_number = 1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', args.port))
    s.listen()
    print(f"Open on port {args.port}")
    while True:
        con, addr = s.accept()
        print(f"New connection from {addr}")
        ClientListener(f"Client_{client_number}", con, args.path).start()
        client_number += 1


if __name__ == '__main__':
    sys.exit(main())
