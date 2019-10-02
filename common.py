# import struct
import pickle

CODE_INIT = 100
CODE_DATA = 101
CODE_END = 102

CODE_INIT_OK = 110
CODE_DATA_OK = 111
CODE_END_OK = 112


class MyPacket:
    def __init__(self, code):
        self.__code = code

    def get_code(self):
        return self.__code

    def serialize(self):
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, packet_bytes):
        return pickle.loads(packet_bytes)


class ResponsePacket(MyPacket):
    def __init__(self, code, message):
        super().__init__(code)
        self.message = message


class InitPacket(MyPacket):
    def __init__(self, filename, filesize):
        super().__init__(CODE_INIT)
        self.filename = filename
        self.filesize = filesize


class DataPacket(MyPacket):
    def __init__(self, data):
        super().__init__(CODE_DATA)
        self.data = data


class CloserPacket(MyPacket):
    def __init__(self):
        super().__init__(CODE_END)

