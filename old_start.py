import socket
from math import ceil
from scapy.all import *
from scapy.all import Raw, IP, TCP, conf
from scapy import plist
from data import Data
from protocol import read, msg_from_id, types, write

global wait, flag
wait = []
flag = False


def adjust_buffer(direction, data):
    global wait
    if not direction:
        l = len(wait)
        for i in range(l):
            if wait[0][0] == data:
                del wait[0]
                return
            elif wait[0][0] in data:
                data = data[len(wait[0][0]):]
                del wait[0]
            elif data in wait[0][0]:
                wait[0][0] = wait[0][0][len(data):]
                return
    return


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
            print("id ", id, "len ", len(buf))
            total += ld
            h = buf.data[:total]
            lenData = int.from_bytes(buf.read(ld), "big")
            if id == 225:
                flag = True
            elif id == 226:
                flag = False
            elif flag == True and not from_client:
                buf.reset()
                return
            if lenData > len(buf) + total:
                raise IndexError
            # if id not in (
            #         3023, 500, 951, 703, 5658, 5572, 700, 153, 6231, 3016, 5809, 3009, 226, 5709, 5708, 3023, 5654,
            #         6135, 862, 882, 883, 221):
            #     c = h + buf.read(lenData)
            #     buf.end()
            #     adjust_buffer(from_client, c)
            #     return
            sdata = buf.read(lenData)
            data = Data(sdata)
        except IndexError:
            buf.reset()
            wait.sort(key=lambda w: w[1])
            for i in wait:
                print(i[1], i[0][:10])
                buf += i[0]
            return "next"
        else:
            if id == 2:
                newbuffer = Buffer(data.readByteArray())
                newbuffer.uncompress()
                msg = Msg.fromRaw(newbuffer, from_client)
                assert msg is not None and not newbuffer.remaining()
                return msg

            buf.end()
            adjust_buffer(from_client, h + sdata)
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
        return msg_from_id[self.id]

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
    global wait
    direction, seq = from_client(pa)
    buf = buf1 if direction else buf2
    id = pa.getlayer(IP).id
    seq = pa.getlayer(TCP).seq
    pa = raw(pa)
    buf += pa
    # print("id ", id, " seq ", seq%2346560526, " len ", len(pa))
    msg = None
    if not direction:
        wait.append([pa, seq])
    while len(buf) > 0 and msg != "next":
        msg = Msg.fromRaw(buf, direction)
        while msg and msg != "next":
            action(msg)
            msg = Msg.fromRaw(buf, direction)


def on_msg(msg):
    Msg.from_json(msg.json())


sniff(filter="ip and host 34.254.78.126 and tcp port 5555", lfilter=lambda p: p.haslayer(Raw),
      prn=lambda p: on_receive(p, on_msg))
