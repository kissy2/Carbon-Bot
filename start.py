import socket
from math import ceil
from scapy.all import sniff
from scapy.all import Raw, IP, TCP
from data import Data
from protocol import read, msg_from_id, types, write,useful,logging
global wait, flag, next_seq, last10
wait, flag, next_seq, last10 = [], 0, False, []
from sys import exc_info
class Buffer(Data):
    def end(self):
        del self.data[: self.pos]
        self.pos = 0

    def reset(self):
        self.__init__()


class Msg:
    def __init__(self, m_id, data, count=None):
        self.id = m_id
        if isinstance(data, bytearray):
            data = Data(data)
        self.data = data
        self.count = count

    def __str__(self):
        ans = str.format(
            "{}(m_id={}, data={}, count={})",
            self.__class__.__name__,
            self.id,
            self.data.data,
            self.count,
        )
        return ans

    def __repr__(self):
        ans = str.format(
            "{}(m_id={}, data={!r}, count={})",
            self.__class__.__name__,
            self.id,
            self.data.data,
            self.count,
        )
        return ans

    @staticmethod
    def fromRaw(buf: Buffer, from_client):
        global wait, flag
        if not buf:
            return
        try:
            header = buf.readUnsignedShort()
            total = 2
            if from_client:
                count = buf.readUnsignedInt()
                total += 4
            else:
                count = None
            id = header >> 2
            ld = header & 3
            total += ld
            lenData = int.from_bytes(buf.read(ld), "big")
            if lenData > len(buf) - total:
                raise IndexError
            # if id not in [3023, 500, 951, 703, 5658, 5572, 700, 153, 780, 6134, 189,
            #               6231, 2, 951, 153, 6231, 3016, 5809, 3009, 226, 5709, 5708, 3023, 5654, 6135, 862, 882, 883, 221]:
            # if id in [428, 6440, 127]:
            #     buf.read(lenData)
            #     buf.end()
            #     return
            data = Data(buf.read(lenData))
        except IndexError:
            buf.pos = 0
            flag+=1
            return "next"
        else:
            if id == 2:
                newbuffer = Buffer(data.readByteArray())
                newbuffer.uncompress()
                msg = Msg.fromRaw(newbuffer, from_client)
                assert msg is not None and not newbuffer.remaining()
                return msg
            buf.end()
            flag=0
            return Msg(id, data, count)

    def lenlenData(self):
        if len(self.data) > 65535:
            return 3
        if len(self.data) > 255:
            return 2
        if len(self.data) > 0:
            return 1
        return 0

    def bytes(self):
        header = 4 * self.id + self.lenlenData()
        ans = Data()
        ans.writeShort(header)
        if self.count is not None:
            ans.writeUnsignedInt(self.count)
        ans += len(self.data).to_bytes(self.lenlenData(), "big")
        ans += self.data
        return ans.data

    @property
    def msgType(self):
        global flag,wait,next_seq
        try:
            return msg_from_id[self.id]
        except:
            print('key error')
            if flag>5:
                print('5 straight erros')
                flag=0
                wait=[]
                next_seq=None
                buf.reset()
            logging.critical(f'Error in start key error {self.id}')


    def json(self):
        if not hasattr(self, "parsed"):
            self.parsed = read(self.msgType, self.data)
        return self.parsed

    @staticmethod
    def from_json(json, count=None, random_hash=True):
        type_name: str = json["__type__"]
        type_id: int = types[type_name]["protocolId"]
        data = write(type_name, json, random_hash=random_hash)
        return Msg(type_id, data, count)


def raw(pa):
    return pa.getlayer(Raw).load


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = input("enter ip adress")
    finally:
        s.close()
    return IP


LOCAL_IP = get_local_ip()


def from_client(pa):
    dst = pa.getlayer(IP).dst
    src = pa.getlayer(IP).src
    if src == LOCAL_IP:
        return True, None
    elif dst == LOCAL_IP:
        return False, pa.getlayer(TCP).seq
    assert False, "Packet origin unknown"


buf1 = Buffer()
buf2 = Buffer()


def on_receive(pa, action):
    global wait, next_seq, last10
    direction, seq = from_client(pa)
    if seq in last10:
        return
    last10 = last10[len(last10) - 9:]
    last10.append(seq)
    pa = raw(pa)
    if not direction:
        buf = buf2
        if seq != next_seq and next_seq:
            wait.append((pa, seq))
            return
        elif wait:
            wait.append([pa, seq])
            wait.sort(key=lambda w: w[1])
            for i in wait:
                buf += i[0]
            next_seq = wait[-1][1] + len(wait[-1][0])
            del wait[:]
        else:
            buf += pa
            next_seq = seq + len(pa)
    else:
        buf = buf1
        buf += pa
    msg = None
    while len(buf) > 0 and msg != "next":
        msg = Msg.fromRaw(buf, direction)
        while msg and msg != "next":
            action(msg)
            msg = Msg.fromRaw(buf, direction)

def on_msg(msg):
    try:
        Msg.from_json(msg.json())
    except:
        print('Error in start')
        logging.info(f'Error in Start {exc_info()}')

