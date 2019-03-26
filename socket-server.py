import socket
import threading
import logging
import datetime

# 封装类 TCP Server
class ChatServer:
    def __init__(self,ip='127.0.0.1',port=9999):
        self.addr = (ip,port)
        self.sock = socket.socket() # 实例化 socket
        self.clients = {} #客户端容器



    def start(self):
        self.sock.bind(self.addr) #绑定端口
        self.sock.listen() #服务启动了
        # 线程启动接受
        threading.Thread(target=self.accept, name='accept').start()

    def accept(self):
        while True:
            s,raddr = self.sock.accept() #阻塞

            # 添加到容器中clients
            self.clients[raddr] = s
            print(s,raddr)
            # 线程启动发送
            threading.Thread(target=self.recv, name='recv',args=(s,raddr)).start()

    def recv(self,sock,addr):
        while True:
            try:
                data = sock.recv(1024) # 阻塞 bytes
            except Exception as e:
                data = b'quit'
            # 判断推出 data == b'quit'
            if data == b'quit':
                self.clients.pop(addr)
                sock.close()
                break

            msg = '{0} {1[0]} {1[1]} {2}'.format(datetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S'),addr,data.decode()).encode()

            # print(data.decode())
            # 群发
            for s in self.clients.values():
                s.send(msg)



    def stop(self):
        for s in self.clients.values():
            s.close()
        self.sock.close()
def main():
    cs = ChatServer()
    cs.start()

    while True:
        cmd = input('>>>')
        if cmd.strip() == 'quit':
            cs.stop()
            threading.Event.wait(4)
            break
        print(threading.enumerate())


if __name__ == '__main__':
    main()