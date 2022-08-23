#computer networks final project
#By: mina mahram/ morva farajzadeh/ zahrafarhadinia

import socket 
import threading


class Server:
    lrmessage=""
    clients=[]
    def __init__(self):
        self.ssocket=None
        self.ServerListening()
   
    def ServerListening(self):
        self.ssocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        local_ip='127.0.0.1'
        local_port=12345
        self.ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssocket.bind((local_ip, local_port))
        print("Server is running, Open the Client Program!")
        
        self.ssocket.listen(5)
        self.MessageRecieving()
    
    def receive_messages(self, soc):
        while True:
            incoming_buffer=soc.recv(1024) 
            if not incoming_buffer:
                break
            self.lrmessage=incoming_buffer.decode('utf-8')
            if self.lrmessage[:6] == "<File>":
                self.lrmessage = self.receive_file(soc, self.lrmessage[6:])
            self.broadcasting(soc)  
        soc.close()
     
    def broadcasting(self, senders_socket):
        for client in self.clients:
            socket, (ip, port)=client
            if socket is not senders_socket:
                socket.sendall(self.lrmessage.encode('utf-8'))

    def MessageRecieving(self):
        while True:
            client=soc, (ip, port)=self.ssocket.accept()
            self.ClientList(client)
            print('Connected to ', ip, ':', str(port))
            t = threading.Thread(target=self.receive_messages, args=(soc,))
            t.start()
            
    def receive_file(self, soc, file_details):
        user_name, file_type, file_name, file_size = file_details.split("<SEPARATOR>")
        file_name = os.path.basename(file_name)
        file_size = int(file_size)
        print("Receiving file: ", file_name, " of size: ", file_size)

        received_bytes = 0
        with open(file_name, "wb") as f:
            while True:

                bytes_read = soc.recv(1024)
                received_bytes += len(bytes_read)
                if received_bytes >= file_size:
                    break

                f.write(bytes_read)


        print(file_name, " received successfully!")
        return f"<File>{user_name}[{file_type}] {os.path.abspath(file_name)}"        
    
    def ClientList(self, client):
        if client not in self.clients:
            self.clients.append(client)


if __name__=="__main__":
    Server()