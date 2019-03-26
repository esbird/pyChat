import socket,threading

addr = ('127.0.0.1',9999)
tcp_client = socket.socket()

tcp_client.connect(addr)

def recv():
    while True:

        data = tcp_client.recv(1024)
        print('收到服务器发来的信息：',data.decode('utf-8'))

threading.Thread(target=recv,name='recv').start()

while True:

    msg = input(">>:").strip()
    if not msg:continue

    if msg == 'quit':
        tcp_client.close()
        break

    tcp_client.send(msg.encode('utf-8'))

    # data = tcp_client.recv(1024)


