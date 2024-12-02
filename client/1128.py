#클라이언트
import socket
import datetime
import random

HOST = "127.0.0.1"
PORT = 5001 #서버 포트
ADDR = (HOST, PORT)
SEP = "|"
BUFSIZE = 1024

def client_program():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)
    print("Connected to the server")
    
    while True:
        print("\nOptions")
        print("1. Create Nickname")
        print("2. Check Nickname Availability")
        print("3. Join chat server")
        print("4. Quit")
        
        choice = input("Enter Your choice: ")
        
        if choice == '1':
            nickname = input("Enter a nickname to create: ")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            client_id = random.randint(0,100000)
            
            # 서버의 IP와 포트를 가져옴
            server_ip, server_port = client_socket.getpeername()
            SERVER = f"{server_ip}:{server_port}"
            
            header = f"CREATE_NICKNAME{SEP}{client_id}{SEP}SERVER{SEP}{timestamp}{SEP}"
            body = f"{len(nickname)} + SEP + {nickname}"
            message = f"{header}{SEP}{body}"
            
            client_socket.send(message.encode())
            
            # 서버 응답 수신
            response = client_socket.recv(BUFSIZE).decode()
            print(f"Server response: {response}")
            
        elif choice == '2':
            nickname = input("Enter a nickname to check: ")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            client_id = random.randint(0,100000)
            
            header = f"CHECK_NICKNAME{SEP}{client_id}{SEP}SERVER{SEP}{timestamp}{SEP}"
            body = f"{len(nickname)} + SEP + {nickname}"
            message = f"{header}{SEP}{body}"
            
            client_socket.send(message.encode())
            
            response = client_socket.recv(BUFSIZE).decode()
            print(f"Server response: {response}")
            
        elif choice == '3':
            nickname = input("Enter your nickname to join: ")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            client_id = random.randint(0,100000)
            
            header = f"JOIN{SEP}{client_id}{SEP}SERVER{SEP}{timestamp}{SEP}"
            body = f"0{SEP}"
            message = f"{header}{SEP}{body}"
            
            client_socket.send(message.encode())
            
            # 서버 응답 수신
            response = client_socket.recv(BUFSIZE).decode()
            print(f"SErver response: {response}")
            
            # 서버로부터 알림 메시지를 수신
            if "SUCCESS" in response:
                print(f"Waiting for server notifications")
                try:
                    while True:
                        server_message = client_socket.recv(BUFSIZE).decode()
                        print(f"Server broadcast: {server_message}")
                except Exception as e:
                    print(f"Disconnected from server {e}")
                    client_socket.close()
                    break
        elif choice == '4':
            nickname = input("Enter your nickname to quit: ").strip()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 메시지 생성
            header = f"QUIT{SEP}{nickname}{SEP}SERVER{SEP}{timestamp}"
            body = f"0{SEP}"
            message = f"{header}{SEP}{body}"
            
            client_socket.send(message.encode())
            print("Disconnected from the server")
            client_socket.close()
            break

        else:
            print("Invalid option. Please try again.")
            
if __name__ == "__main__":
    client_program()