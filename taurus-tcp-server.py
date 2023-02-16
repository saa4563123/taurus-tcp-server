import socket
import socketserver
import threading
from datetime import datetime

version = '1.0' # 소프트웨어 버전
HOST = 'local.nura.kr' # 서버 ip
PORT = 9009 # 서버 포트
lock = threading.Lock()

class UserManager:
    def __init__(self):
        self.users = {} # 사용자 정보
    
    # 사용자 등록 함수
    def addUser(self, username, conn, addr):
        if username in self.users:
            conn.send('[TAURUS] 이미 연결된 닉네임 입니다.\n'.encode())
            return None

        lock.acquire()
        self.users[username] = (conn, addr)
        lock.release()

        self.sendMessageToAll('[TAURUS] [%s]님이 입장했습니다!' % username)
        print('[TAURUS] 서버 접속자 수 [%d]' % len(self.users))

        return username
    
    # 사용자 제거 함수
    def removeUser(self, username):
        if username not in self.users:
            return

        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[TAURUS] [%s]님이 퇴장했습니다.' % username)
        print('[TAURUS] 서버 접속자 수 [%d]' % len(self.users))

    def messageHandler(self, username, msg):
        if msg[0] != '/':  # 명령어 구분
            self.sendMessageToAll('[%s] %s' % (username, msg))
            return
       
        if msg.strip() == '/quit': # 퇴장 명령어
            self.removeUser(username)
            return -1

    # 전체 메시지 전송 함수
    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    def handle(self): # 접속시 클라이언트 주소 출력
        print('[TAURUS] [%s] 연결됨' % self.client_address[0])

        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print('[%s] ' % username, end='')
                print(msg.decode())
                if self.userman.messageHandler(username, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)

        except Exception as e:
            print(e)

        print('[TAURUS] [%s] 접속종료' % self.client_address[0])
        self.userman.removeUser(username)

    def registerUsername(self):
        while True:
            self.request.send('===========================================================\n'
                              '[TAURUS] 서버에 접속하였습니다.\n'
                              '[TAURUS] Projectile Data Server. KNUT TAURUS 2023\n'
                              '[TAURUS] Create By - Lee SeungHwan.\n'
                              '[TAURUS] 사용하실 사용자 이름을 작성해주세요.\n'
                              '===========================================================\n'.encode())
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username, self.request, self.client_address):
                return username

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# 자동 서버 아이피 지정 함수
def ipset():
    subHOST = socket.gethostbyname(socket.gethostname())

    return subHOST

def runServer():
    print('===========================================================')
    print('[TAURUS] 서버를 시작합니다. Version - %s' % version)
    print('[TAURUS] 서버 호스트 도메인 - %s' % HOST)
    print('[TAURUS] 서버 호스트 포트 - %s' % PORT)
    print('[TAURUS] 서버를 끝내려면 Ctrl-C를 누르세요.')
    print('[TAURUS] Create by - Lee SeungHwan. KNUT TAURUS 2023')
    print('===========================================================')

    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('===========================================================')
        print('[TAURUS] 서버를 종료합니다.')
        print('[TAURUS] Server Shutdown...')
        print('===========================================================')
        server.shutdown()
        server.server_close()

HOST = ipset()
runServer()
