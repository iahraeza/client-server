#computer networks final project
#By: morva farajzadeh/ mina mahram/  zahrafarhadinia

import socket 
import threading
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox
from tkinter import filedialog
import os
import mimetypes

class GUI:
    csocket=None
    lrmessage=None
    def __init__(self, master):
        self.root=master
        
        self.chat_box=None
        self.name_box=None
        self.enter_text=None
        self.join_button=None
        self.file_button = None
        
        self.SocketInitializing()
        self.initialize_gui()
        self.lMessagrLisitening()

    def SocketInitializing(self):
        self.csocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        
        rip='127.0.0.1'  
        rport=12345
        
        self.csocket.connect((rip, rport)) 

    def initialize_gui(self): 
        self.root.resizable(0, 0)
        self.root.title("Final Project - Socket Chat") 
        self.ChatBox()
        self.Name()
        self.ChatEntryBox()

    def lMessagrLisitening(self):
        thread=threading.Thread(target=self.MessageRecieving, args=(self.csocket,)) 
        thread.start()
    
    def MessageRecieving(self, soc):
        while True:
            buffer=soc.recv(1024)
            if not buffer:
                break
            message=buffer.decode('utf-8')
            if "joined" in message:
                user=message.split(":")[1]
                message=user+" has joined"
                self.chat_box.insert('end',message+'\n')
                self.chat_box.yview(END)
                
            elif "<File>" in message:
                message = message[6:]                
                self.chat_box.insert('end', message + '\n')
                self.chat_box.yview(END)
                file_type = message[message.find('['):message.find(']')+1]                
                last_line = int(self.chat_box.index('end').split('.')[0]) - 2
                self.chat_box.tag_add(file_type, f'{last_line}.{message.find("[")}', f'{last_line}.{message.find("]")}')
                self.chat_box.tag_config(file_type, foreground=self.file_collor(file_type))
            else:
                self.chat_box.insert('end',message+'\n')
                self.chat_box.yview(END)

        soc.close()

    def Name(self):
        frame=Frame()
        Label(frame, text='Name/Nikname:', font=("Arial", 14)).pack(side='left', padx=10)
        self.name_box=Entry(frame, width=40, borderwidth=2, bg="lightgray")
        self.name_box.pack(side='left', anchor='e')
        self.join_button=Button(frame, text="Join", width=10, command=self.Join, bg="lightpink").pack(side='left')
        self.file_button=Button(frame, text="File", width=10, command=self.send_file ,bg="lightgreen").pack(side='left')
        frame.pack(side='top', anchor='nw')

    def ChatBox(self):
        frame=Frame()
        Label(frame, text='Chat Room:',bg="lightgray", font=("Arial", 12)).pack(side='top', anchor='w')
        self.chat_box = Text(frame, width=60, height=10, font=("Arial", 12),bg="lightblue")
        scrollbar=Scrollbar(frame, command=self.chat_box.yview, orient=VERTICAL)
        self.chat_box.config(yscrollcommand=scrollbar.set)
        self.chat_box.bind('<KeyPress>', lambda e: 'break')
        self.chat_box.pack(side='left', padx=11)
        scrollbar.pack(side='left', fill='y')
        frame.pack(side='top')

    def ChatEntryBox(self):
        frame=Frame()
        Label(frame, text='Enter message:', font=("Arial", 14)).pack(side='top', anchor='w')
        self.enter_text=Text(frame, width=60, height=3, font=("Arial", 12),bg="lightblue")
        self.enter_text.pack(side='left', pady=15)
        self.enter_text.bind('<Return>', self.keyPressing)
        frame.pack(side='top')

    def Join(self):
        if len(self.name_box.get())==0:
            messagebox.showerror(
                "Error!", "Please enter your name ")
            return
        self.name_box.config(state='disabled')
        self.csocket.send(("joined:"+self.name_box.get()).encode('utf-8'))

    def keyPressing(self, event):
        if len(self.name_box.get())==0:
            messagebox.showerror("Error!", "Please enter your name ")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text.delete(1.0, 'end')

    def send_chat(self):
        senders_name=self.name_box.get().strip()+": "
        data=self.enter_text.get(1.0, 'end').strip()
        message=(senders_name+data).encode('utf-8')
        self.chat_box.insert('end', message.decode('utf-8')+'\n')
        self.chat_box.yview(END)
        self.csocket.send(message)
        self.enter_text.delete(1.0, 'end')
        return 'break'

    def send_file(self):
        
        
        if 'disabled' not in self.name_box.configure('state'):
            messagebox.showerror(
                "Error!", "Please enter your name ")
            return
        
        senders_name = self.name_box.get().strip() + ": "
        file_name = filedialog.askopenfilename()
        file_type = self.check_file_type(file_name)
        if len(file_name) == 0:
            return
        self.chat_box.insert(
            'end', senders_name + '[' + file_type + '] ' + file_name + '\n')
        self.chat_box.yview(END)
        last_line = int(self.chat_box.index('end').split('.')[0]) - 2
        self.chat_box.tag_add(file_type, f'{last_line}.{len(senders_name)}', f'{last_line}.{len(senders_name)+len(file_type)+2}')
        self.chat_box.tag_config(file_type, foreground=self.file_collor(file_type))
        
        self.csocket.send(
            f"<File>{senders_name}<SEPARATOR>{file_type}<SEPARATOR>{file_name}<SEPARATOR>{os.path.getsize(file_name)}".encode())
        with open(file_name, "rb") as f:
            while True:
                bytes_read = f.read(256)
                if not bytes_read:
                    break

                self.csocket.sendall(bytes_read)

    def check_file_type(self, file_name):
        return mimetypes.guess_type(file_name)[0]

    def file_collor(self, type):
        if 'text' in type:
            return 'blue'
        elif 'image' in type:
            return 'green'
        elif 'video' in type:
            return 'blue'
        elif 'audio' in type:
            return 'orange'
        else:
            return 'black'

    def CloseWindow(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.csocket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.CloseWindow)
    root.mainloop()