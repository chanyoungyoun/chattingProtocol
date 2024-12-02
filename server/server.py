import datetime
import socket # 소켓 통신을 위한 라이브러리
from threading import Thread, Event # 멀티스레딩과 이벤트


event = Event()
HOST = "127.0.0.1"
PORT = 5001 #서버 포트
ADDR = (HOST, PORT)
SEP = "|"
BUFSIZE = 1024

nicknames = {} # 닉네임 저장소
clients = [] # 연결된 클라이언트 소켓 리스트


def broadcast(message, exclude_socket = None):
    """
       모든 클라이언트에게 메시지를 전송 (특정 소켓 제외 기능)
    """
    for client in clients:
        if client != exclude_socket:
            try:
                client.send(message.encode())
            except Exception as e:
                print(f"Broadcast error: {e}")
                client.close()
                clients.remove(client)

# 클라이언트 메시지 처리
def handle_client(client_socket, addr):
    """
    클라이언트 메시지 처리
    """
    nickname = None
    while True:
        try:
            msg = client_socket.recv(BUFSIZE).decode() # 클라이언트한테 데이터 받고 디코딩
            print(f"Received message from {addr}: {msg}")
            
            # 메시지 검증 및 분리
            parts = msg.split(SEP, maxsplit=4)
            if len(parts) != 5:
                raise ValueError(f"Incomplete message received: {msg}")
            
            header = parts[:4]
            body = parts[4]
            method, sender, receiver, timestamp = header

            # 바디 검증 및 분리
            if SEP in body:
                body_parts = body.split(SEP, maxsplit=1)
                if len(body_parts) == 2:
                        message_length, message = body_parts
                else:
                    raise ValueError(f"Invaild body format: {body}")
                message_length, message = body_parts
            else:
                raise ValueError(f"Missing separator in body: {body}")
            
            message_length, message = body.split(SEP)
            
            if method == "CREATE_NICKNAME":
                if message in nicknames : # 중복 확인
                    response = f"CREATE_NICKNAME_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}FAIL: Invalid nickname"
                else :
                    nicknames[message] = client_socket
                    response = f"CREATE_NICKNAME_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}SUCCESS: {message}"
                client_socket.send(response.encode())
                
            elif method == "CHECK_NICKNAME": # 닉네임 중복 여부 확인 요청
                if message in nicknames: # 닉네임이 이미 존재하는 경우
                    response = f"CREATE_NICKNAME_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}5{SEP}TAKEN"
                else: # 닉네임 사용 가능 경우
                    response = f"CREATE_NICKNAME_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}9{SEP}AVAILABLE"
                client_socket.send(response.encode())
                    
            elif method == "QUIT":
                if message in nicknames :
                    del nicknames[message] # 닉네임 저장소에서 삭제
                    response = f"QUIT_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}16{SEP}SUCCESS: {message} disconnected"
                else:
                    response = f"QUIT_REPLY{SEP}SERVER{SEP}{sender}{SEP}{timestamp}{SEP}20{SEP}ERROR: Nickname no found"
                client_socket.send(response.encode())
                client_socket.close()
                break
            
            elif method == "JOIN":
                nickname = sender
                if nickname in nicknames:
                    # 닉네임 중복 에러 응답
                    response = f"JOIN_REPLY{SEP}SERVER{SEP}{nickname}{SEP}{timestamp}{SEP}18{SEP}FAIL: Nickname already exists"
                elif len(clients) >= 10: # 최대 10명 제한
                    # 서버 풀 에러 응답
                    response = f"JOIN_REPLY{SEP}SERVER{SEP}{nickname}{SEP}{timestamp}{SEP}18{SEP}FAIL: Server full"
                else:
                    # 성공 응답 및 닉네임 등록
                    nicknames[nickname] = client_socket
                    clients.append(client_socket)
                    response = f"JOIN_REPLY{SEP}SERVER{SEP}{nickname}{SEP}{timestamp}{SEP}24{SEP}SUCCESS: Welcome!"
                    
                    # 다른 클라이언트에게 접속 알림
                    broadcast_message = f"NOTICE{SEP}SERVER{SEP}ALL{SEP}{timestamp}{SEP}25{SEP}{nickname} has joined"
                    broadcast(broadcast_message, exclude_socket = client_socket)
                    
                client_socket.send(response.encode())
        
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            if nickname:
                if nickname in nicknames:
                    del nicknames[nickname]
                if client_socket in clients:
                    clients.remove(client_socket)
                # 접속 종료 알림
                leave_message = f"NOTICE{SEP}SERVER{SEP}ALL{SEP}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{SEP}25{SEP}{nickname} has left"
                broadcast(leave_message, exclude_socket = client_socket)
            client_socket.close()
            break

def accept_clients():
    """
    클라이언트 연결 수락
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR) # IP 포트와 바인딩
    server_socket.listen(5)
    print("Server is running and waiting for connections")

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"Client connected: {client_addr}")
        
        # 스레드 생성
        client_thread = Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.daemon = True
        client_thread.start()
    
if __name__ == "__main__":
    accept_clients()
    