#coding:utf-8

import threading
import hashlib
import socket
import base64
import struct

global clients
clients = {}

#生成发送内容
def write_msg(message):
    data = struct.pack('B',129) #写入第一个字节 ，10000001

    # 写入包长
    msg_len = len(message.encode())
    if msg_len <= 125:
        data += struct.pack('B',msg_len)
    elif msg_len <= (2**16 -1):
        data += struct.pack('!BH',126, msg_len)
    elif msg_len <= (2**64 -1):
        data += struct.pack('!BQ',127, msg_len)
    else:
        print('message too large')
        return
    data += message.encode()
    return  data

# 通知客户端
def notify(message):
    for connection in clients.values():
        connection.send(write_msg(message))


# 客户端处理线程
class websocket_thread(threading.Thread):
    def __init__(self, connection, username):
        super(websocket_thread, self).__init__()
        self.connection = connection
        self.username = username

    def run(self):
        print('new websocket client joined!')

        data = self.connection.recv(1024)
        headers = self.parse_headers(data.decode('utf-8'))
        token = self.generate_token(headers['Sec-WebSocket-Key'])
        msg = '\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: {}\r\n\r\n'.format(token.decode()).encode()
        self.connection.send(msg)
        while True:
            try:
                data = self.connection.recv(1024)
            except socket.error as e:
                print("unexpected error: ", e)

                clients.pop(self.username)
                break
            data = self.parse_data(data)
            if len(data) == 0:
                continue
            message = self.username + ": " + data
            notify(message)

    def parse_data(self, msg):
        print(msg)
        v = msg[1] & 127
        if v == 126:
            p = 4
        elif v == 127:
            p = 10
        else:
            p = 2
        mask = msg[p:p + 4]
        data = msg[p + 4:]

        raw_str = ''
        for k, v in enumerate(data):
            raw_str += chr(v ^ mask[k % 4])
        print(raw_str)
        return raw_str

    def parse_headers(self, msg):
        headers = {}
        header, data = msg.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, value = line.split(': ', 1)
            headers[key] = value
        headers['data'] = data
        return headers

    def generate_token(self, msg):
        key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key.encode()).digest()
        return base64.b64encode(ser_key)


# 服务端
class websocket_server(threading.Thread):
    def __init__(self, port):
        super(websocket_server, self).__init__()
        self.port = port

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(5)
        print('websocket server started!')

        while True:
            connection, address = self.sock.accept()
            try:
                username = "ID" + str(address[1])
                thread = websocket_thread(connection, username)
                thread.start()
                clients[username] = connection
            except socket.timeout:
                print('websocket connection timeout!')
    def stop(self):
        for con in clients.values():
            con.close()
        self.sock.close()



if __name__ == '__main__':
    server = websocket_server(9000)
    server.start()
    while True:
        cmd = input('>>>')
        if cmd.strip() == 'quit':
            server.stop()
            threading.Event.wait(4)
            break
        print(threading.enumerate())