#!/usr/bin/python

# imports
import os, sys, tkFileDialog, threading, signal, tkMessageBox, random
from socket import *
from datetime import *
from time import *
from Tkinter import *
try:
    os.stat('logs')
except:
    os.mkdir('logs')


def GetIP():
    ip = gethostbyname(gethostname())
    if '127.' in ip:
        ip = ([l for l in ([ip for ip in gethostbyname_ex(gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket()]][0][1]]) if l][0][0])
    return ip

def TimeStamps():
    return datetime.fromtimestamp(time()).strftime('(%H:%M:%S) ')
def TimeStampsDate():
    return datetime.fromtimestamp(time()).strftime('%d-%m-%Y')

serverIP = ''
serverPORT = 7000
nickname = 'Guest'
for rand in range(4):
    nickname += str(random.randint(0,9))


log_file = 'logs\\' + TimeStampsDate() + '.txt'
Sendbox = []
client_ip = GetIP()
key = '1234'
separate = chr(173)
chkbox = False
chkbox2 = True
buffer = 1024
config_file = 'settings.txt'


def LoadSettings():
    global serverIP, serverPORT, nickname, key, buffer
    if os.path.isfile(config_file) and os.path.getsize(config_file) != 0:
        f_settings = open(config_file, 'r')
        settings = f_settings.read().split('\n')
        f_settings.close()
        for i in settings:
            if 'Default_Server' in i:
                serverIP = i.split('=')[1].strip(' ')
            elif 'Default_Port' in i:
                serverPORT = int(i.split('=')[1].strip(' '))
            elif 'Nickname' in i:
                nickname = i.split('=')[1].strip(' ')
            elif 'Key' in i:
                key = i.split('=')[1].strip(' ')
            elif 'Buffer' in i:
                buffer = int(i.split('=')[1].strip(' '))
            else:
                print '>> Error while loading settings'
    else:
        f_settings = open(config_file, 'w')
        f_settings.write('Default_Server = ')
        f_settings.write('\nDefault_Port = ' + str(serverPORT))
        f_settings.write('\nNickname = ' + nickname)
        f_settings.write('\nKey = ' + str(key))
        f_settings.write('\nBuffer = ' + str(buffer))
        f_settings.close()
LoadSettings()

def SaveSettings(key, value):
    f_settings = open(config_file, 'r')
    settings = f_settings.read().split('\n')
    f_settings.close()
    for i in settings:
        if key in i:
            settings.remove(i)
    f_settings = open(config_file, 'w')
    f_settings.write('\n'.join(settings))
    f_settings.write('\n' + key + ' = ' + str(value))
    f_settings.close()

def Generate_key(key):
    try:
        global encrypted_key
        k = ''
        for i in key:
            k += str(ord(i))
        encrypted_key = int(k)
        return encrypted_key
    except:
        Sendbox.append(">> Encryption Error: Key not entered in field")


welcome_msg = '# Welcome ' + nickname + "\n# Press 'Connect' to start chat session"
welcome_msg += '\n# Default Server: ' + serverIP + ':' + str(serverPORT)
welcome_msg += '\n# Default key: ' + key + ' (Encrypted: ' + str(Generate_key(key)) + ')\n'

def Log(data):
    global log_file
    f = open(log_file, 'a')
    f.write(data + '\n')
    f.close()
    Sendbox.append(data)

def CleanLog():
    global log_file
    if os.path.isfile(log_file):
        os.remove(log_file)
        Sendbox.append('>> Log file: ' + log_file + ' has been deleted')
    else:
        Sendbox.append('>> Error #3250: ' + log_file + ' is not exist')

def OpenFile(log_file):
    if os.path.isfile(log_file):
        os.startfile(log_file)
    else:
        Sendbox.append('>> Error #3251: ' + log_file + ' is not exist')

def LoadLog():
    global log_file
    file = open(log_file, 'r')
    read_file = file.read()
    file.close()
    return read_file

def Send(data):
    global client_s
    try:
        if chkbox2 == True and data != '#EXIT#':
            client_s.send(Encrypt(data))
        else:
            client_s.send(data)
        Log(TimeStamps() + data)
    except:
        Sendbox.append('>> Error #5435: No server connection')

def Change_name(old_name, new_name):
    global nickname
    if nickname != new_name:
        nickname = new_name
        SaveSettings('Nickname', nickname)
        log_msg = old_name + ' changed his nickname to ' + new_name
        try:
            Send(log_msg)
        except:
            pass
    else:
        Sendbox.append('>> Nickname is already set to ' + new_name)

def ChangeLogfile(new_name):
    global log_file
    if log_file != new_name:
        log_file = new_name
        Sendbox.append('>> Log file has been set to: ' + new_name)
    else:
        Sendbox.append('>> Error #1255: Logfile is already set to ' + new_name)

def Encrypt(data):
    enlist, EncryptedTxt = [], ''
    for i in data:
        i = ord(i) + encrypted_key
        enlist.append(str(i))

    for i in enlist:
        EncryptedTxt += separate + i
    return EncryptedTxt

def Decrypt(data):
    saved_data = data
    try:
        # data1 = ''.join(data.split(': ')[0])
        # data2 = ''.join(data.split(': ')[1:])
        data2 = data.split(separate)
        data2.remove('')
        delist, DecryptedTxt = [], ''
        try:
            for i in data2:
                i = int(i) - encrypted_key
                i = chr(i)
                delist.append(i)

            for i in delist:
                DecryptedTxt += i

            # DecryptedTxt = data1 + ': ' + DecryptedTxt
            return DecryptedTxt
        except:
            print '>> Error: Wrong key'
    except:
        return saved_data

#### GUI code

def init(top, gui):
    global w, top_level, TkObject
    w = gui
    top_level = top
    TkObject = top

def vp_start_gui():
    global w, TkObject, top
    TkObject = Tk()
    top = Chat_GUI(TkObject)
    init(TkObject, top)
    try:
        TkObject.iconbitmap(default='chat.ico')
    except:
        print ">> Error #3224: 'chat.ico' is missing"
    TkObject.resizable(width=False, height=False)
    TkObject.mainloop()
w = None

kill = 0


class Chat_GUI():
    def __init__(self, top=None):
        def StartLog():
            try:
                clear_file = open(log_file, 'a')
                clear_file.close()
                record = "# Start recording log: '" + log_file + "'"
                Sendbox.append(record)
            except:
                print '>> Logs folder is missing, creating folder...'
                os.mkdir('logs')
                record = "# Start recording log: '" + log_file + "'"
                Sendbox.append(record)
        StartLog()

        def Connect(serverIP, serverPORT, disconnect):
            serverIPPort = serverIP + ':' + str(serverPORT)
            SaveSettings('Default_Server', serverIP)
            SaveSettings('Default_Port', serverPORT)
            if disconnect != 1:
                global client_s
                try:
                    print '>> Connecting to', str(serverIPPort) + '...'
                    client_s = socket()
                    client_s.connect((serverIP, serverPORT))
                    thread_receive = threading.Thread(target= Receive).start()
                    client_s.send(nickname + '# #IDENT# #' + client_ip + '# #' + str(buffer))
                    Sendbox.append('>> Connected to server (' + serverIPPort + ')')
                    # Receive()
                except:
                    Sendbox.append('>> Error 3249: Server ' + serverIPPort + ' is down.')
            else:
                try:
                    client_s.close()
                    kill = 1
                    Sendbox.append('>> Disconnected from server (' + serverIPPort + ')')
                except:
                    Sendbox.append('# >> Unexpected Error #1211: You already disconnected')

        def Receive():
            global kill, client_s, w
            kill = 0
            while kill != 1:
                sleep(0.01)
                data_received = client_s.recv(buffer)
                try:
                    data_received = Decrypt(data_received)
                except:
                    pass

                if '#MOTD#' in data_received:
                    Sendbox.append('>> MOTD:\n' + ''.join(data_received.split('#MOTD#')[1:]) + '\n')
                    if int(data_received.split('#MOTD#')[0]) != buffer:
                        Sendbox.append(">> Error #1221: Server buffer doesn't  match client buffer")

                elif 'PONG' in data_received:
                    timenow = datetime.now().strftime("(%H:%M:%S.%f) ")
                    print timenow + '>> Received: PONG'
                    Sendbox.append(">> Connecting Check: Pong has been received, Connection OK")

                elif 'USERLIST' in data_received:
                    try:
                        if nickname not in data_received:
                            print '>> USERLIST: ', data_received.split('#')[0], ' is ask who is here?'
                            client_s.send(nickname + ' is here.')
                    except socket.timeout:
                        Sendbox.append('>> USERLIST Error: Connection timeout')

                elif ' is here' in data_received:
                        if nickname not in data_received:
                            Sendbox.append(data_received)

                elif 'INCOMING_FILE' in data_received:
                    if chkbox == False:
                        pass
                    else:
                        if nickname in data_received:
                            pass
                        else:
                            print 'File transfer has recognized'
                            file_details = data_received.split('# #')
                            file_size = file_details[1]
                            file_sender = file_details[2] + ' (' + file_details[3] + ')'
                            file_name = file_details[4]
                            file_msg = 'File name: ' + file_name + '\nFile size: ' + str(file_size)
                            file_msg += '\nSent by: ' + file_sender + '\n'
                            Sendbox.append(file_msg)
                            FULLDATA = ''

                elif 'START FILE TRANSFER' in data_received:
                    file_size = int(data_received.split('# #')[1])
                    file = open(path_to_send, 'rb')
                    for buff in range(0,file_size, buffer):
                        data = file.read(buffer)
                        client_s.send(data)
                    file.close()
                    client_s.send('END_FILE')
                    Sendbox.append('>> File ' + path_to_send.split('/')[-1] + ' has been sent successfully')

                elif 'END_FILE' in data_received:
                    if chkbox == False:
                        pass
                    else:
                        if nickname in data_received:
                            pass
                        else:
                            incoming_file = open('Files\\' + file_name, 'wb')
                            incoming_file.write(FULLDATA)
                            incoming_file.close()
                            Sendbox.append('>> File has been received successfully')

                elif data_received:
                    data_received_ts = TimeStamps() + data_received
                    Log(data_received_ts)
                else:
                    pass

        def UpdateScreen():
            while True:
                sleep(0.01)
                if len(Sendbox) != 0:
                    self.output.configure(state='normal')
                    if 'Error' in Sendbox[-1]:
                        self.output.tag_configure('color-red', foreground='red')
                        self.output.insert(END, Sendbox[-1] + '\n', 'color-red')
                    elif 'MOTD' in Sendbox[-1]:
                        self.output.tag_configure('color-purple4', foreground='purple4')
                        self.output.insert(END, Sendbox[-1] + '\n', 'color-purple4')
                    elif 'log' in Sendbox[-1]:
                        self.output.tag_configure('color-brown4', foreground='brown4')
                        self.output.insert(END, Sendbox[-1] + '\n', 'color-brown4')

                    elif 'changed his nickname to' in Sendbox[-1] or 'joined' in Sendbox[-1] or 'Connected' in Sendbox[-1]:
                        self.output.tag_configure('color-green4', foreground='green4')
                        self.output.insert(END, Sendbox[-1] + '\n', 'color-green4')
                    elif nickname in Sendbox[-1]:
                        self.output.tag_configure('color-blue', foreground='blue')
                        self.output.insert(END, Sendbox[-1] + '\n', 'color-blue')
                    else:
                        self.output.insert(END, Sendbox[-1] + '\n')

                    self.output.pack()
                    self.output.configure(state='disabled')
                    self.output.see("end")
                    Sendbox.remove(Sendbox[-1])


        def ChangeClient(oldip):
            newip = self.Entry_clientip.get()
            global client_ip
            if oldip != newip:
                client_ip = newip
                Sendbox.append('>> New Client IP ' + newip + ' has been set.')
            else:
                Sendbox.append('>> Error: Client IP ' + newip + ' is already defined')

        def SendBtn(arg):
            send_button = self.Entry_nickname.get() + ': ' + self.Entry_message.get()
            Send(send_button)
            self.Entry_message.delete(0, END)

        def ConnectTo():
            take_ip = self.Entry_server.get()
            take_port = int(self.Entry_port.get())
            Connect(take_ip, take_port, 0)
            self.Frame_output.configure(text=' Chat:  [ Connected to: ' + take_ip + ' : ' + str(take_port) + ' ]')

        def Disconnect():
            take_ip = self.Entry_server.get()
            take_port = int(self.Entry_port.get())
            Connect(take_ip, take_port, 1)
            self.Frame_output.configure(text=' Chat:  [ Disconnected ]')

        def CheckCon():
            global client_s
            try:
                timenow = datetime.now().strftime("(%H:%M:%S.%f)")
                Sendbox.append('>> Connecting Check: Sending ping to the server...')
                client_s.send('#PING#')
                print timenow + " >> Send: PING"
            except:
                Sendbox.append('>> Error #8436: Connection check failed - No server connection')

        def Go_nickname():
            Change_name(nickname, self.Entry_nickname.get())

        def ChangeKey(new_key):
            global key
            SaveSettings('Key', new_key)
            if key != new_key:
                enc_key = Generate_key(self.Entry_key.get())
                if enc_key:
                    Sendbox.append('>> New key: ' + new_key + ' (Encrypted: ' + str(enc_key) + ') has been set.')
                    key = new_key
                    if chkbox2 == True:
                        self.Check_dataencrypt.configure(text = 'Data encryption: Enabled       Key: ' + key)
                    else:
                        self.Check_dataencrypt.configure(text = 'Data encryption: Disabled      Key: ' + key)

            else:
                Sendbox.append('>> Error: key ' + new_key + ' is already defined')

        def WhoIsHere():
            global client_s
            try:
                client_s.send(nickname + '#USERLIST#')
                Sendbox.append('>> Who is here?')
            except:
                Sendbox.append('>> Error #1251: Cant find who is here - No server connection.')

        def SelectFile():
            file_path = tkFileDialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("Pictures","*.png *.jpg *.jpeg *.gif "), ("All files", "*")))
            self.Entry_file.delete(0, END)
            self.Entry_file.insert(END, file_path)

        def SendFile(file_fullpath):
            global path_to_send, file_size
            path_to_send = file_fullpath
            if file_fullpath == '':
                Sendbox.append(">> Error #9421: You didn't chose a file")
            else:
                file_size = os.path.getsize(file_fullpath)
                if file_size == 0:
                        Sendbox.append('>> File transfer Error: Empty file has selected.')
                else:
                    try:
                        global client_s
                        file_name = file_fullpath.split('/')[-1]        # split the path from the filename
                        header_msg = 'INCOMING_FILE# #' + str(file_size) + '# #' + nickname + '# #' + client_ip + '# #' + file_name + '# #' + str(buffer)
                        client_s.send(header_msg)
                    except:
                        Sendbox.append('>> Error #2120: No server connection')




        def UpdateCheckbox():
            global chkbox
            if chkbox == False:
                chkbox = True
                self.Check_autorecv.configure(text='Receive files: Enabled')
            else:
                chkbox = False
                self.Check_autorecv.configure(text='Receive files: Disabled')

        def UpdateCheckbox2():
            global chkbox2
            if chkbox2 == False:
                chkbox2 = True
                self.Check_dataencrypt.configure(text='Data encryption: Enabled       Key: ' + key)
            else:
                chkbox2 = False
                self.Check_dataencrypt.configure(text='Data encryption: Disabled      Key: ' + key)


        def Quit():
            try:
                Send('#EXIT#')
                client_ip.close()
            except:
                pass
            print 'bye :)'
            os.kill(os.getpid(), signal.SIGTERM)

        def callback():
            if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
                Quit()

        top.geometry("979x677+400+179")
        top.title("Chat client")
        top.bind('<Escape>', lambda e: callback())
        top.protocol("WM_DELETE_WINDOW", callback)

        self.Frame_top = Frame(top)                                             # TOP frame
        self.Frame_top.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.Frame_top.configure(relief=GROOVE, borderwidth="14", width=975)

        self.Frame_output = LabelFrame(self.Frame_top)                          # Chat - LabelFrame (left side)
        self.Frame_output.place(relx=0.01, rely=0.01, relheight=0.88, relwidth=0.73)
        self.Frame_output.configure(relief=GROOVE, borderwidth="3", width=715, text=' Chat:')

        self.scrollbar = Scrollbar(self.Frame_output)
        self.scrollbar.pack(side = 'right',fill='y')

        self.output = Text(self.Frame_output, width=84, height=33.5, yscrollcommand=self.scrollbar.set)     # OUTPUT - Text
        self.output.place(relx=0.0, rely=0.0, relheight=1, relwidth=0.975)
        self.output.configure(state='normal')
        self.output.insert(END, welcome_msg)
        self.output.configure(state='disabled')
        self.thread_output = threading.Thread(target=UpdateScreen)
        self.thread_output.start()

        self.Entry_message = Entry(self.Frame_top)                              # Text to send - Entry
        self.Entry_message.place(relx=0.01, rely=0.905, height=30, relwidth=0.6)
        self.Entry_message.configure(font="TkFixedFont")
        self.Entry_message.insert(END, 'Hi')
        self.Entry_message.bind('<Return>', SendBtn)

        self.Button_submit = Button(self.Frame_top)                             # Submit - Button
        self.Button_submit.place(relx=0.62, rely=0.905, height=30, width=110)
        self.Button_submit.configure(text='Submit')
        self.Button_submit.configure(command=lambda: SendBtn(''))


        self.Frame_R = LabelFrame(self.Frame_top)                               # Settings - LabelFrame (right side)
        self.Frame_R.place(relx=0.75, rely=0.01, relheight=0.95, relwidth=0.24)
        self.Frame_R.configure(text=' Settings:')

        self.XButton = Button(self.Frame_top)                                   # Quit 'X' - Button
        self.XButton.place(relx=0.75, rely=0.96, relheight=0.03, relwidth=0.236)
        self.XButton.configure(text= 'Exit', command=lambda: Quit())

        self.Label_server = Label(self.Frame_R)                                 # Server - Label
        self.Label_server.place(relx=0.25, rely=0.005, height=21, width=34)
        self.Label_server.configure(text='Server:')

        self.Entry_server = Entry(self.Frame_R)                                 # Server - Entry
        self.Entry_server.place(relx=0.04, rely=0.04, height=28, relwidth=0.60)
        self.Entry_server.configure(background="white", font="TkFixedFont")
        self.Entry_server.insert(END, serverIP)

        self.Label_port = Label(self.Frame_R)                                   # Port - Label
        self.Label_port.place(relx=0.71, rely=0.005, height=21, width=34)
        self.Label_port.configure(text='Port')

        self.Entry_port = Entry(self.Frame_R)                                   # Port - Entry
        self.Entry_port.place(relx=0.7, rely=0.04, height=28, relwidth=0.23)
        self.Entry_port.configure(background="white", font="TkFixedFont")
        self.Entry_port.insert(END, serverPORT)

        self.Label_clientip = Label(self.Frame_R)                               # Client IP - Label
        self.Label_clientip.place(relx=0.255, rely=0.09, height=24, width=34)
        self.Label_clientip.configure(text='Client:')

        self.Entry_clientip = Entry(self.Frame_R)                               # Client IP - Entry
        self.Entry_clientip.place(relx=0.04, rely=0.125, height=28, relwidth=0.60)
        self.Entry_clientip.configure(background="white", font="TkFixedFont")
        self.Entry_clientip.insert(END, client_ip)

        self.Button_clientip = Button(self.Frame_R)                             # Client IP 'GO' - Button
        self.Button_clientip.place(relx=0.7, rely=0.125, height=28, relwidth=0.23)
        self.Button_clientip.configure(text='Go')
        self.Button_clientip.configure(command=lambda: ChangeClient(client_ip))

        self.Button_connect = Button(self.Frame_R)                              # Connect - Button
        self.Button_connect.place(relx=0.05, rely=0.19, height=25, width=195)
        self.Button_connect.configure(text='Connect')
        self.Button_connect.configure(command=lambda: ConnectTo())

        self.Button_disconnect = Button(self.Frame_R)                           # Disconnect - Button
        self.Button_disconnect.place(relx=0.05, rely=0.25, height=25, width=195)
        self.Button_disconnect.configure(text='Disconnect')
        self.Button_disconnect.configure(command=lambda: Disconnect())

        self.Button_ping = Button(self.Frame_R)                                 # Ping - Button
        self.Button_ping.place(relx=0.05, rely=0.31, height=30, width=90)
        self.Button_ping.configure(text='Ping', command=lambda: CheckCon())

        self.Button_userlist = Button(self.Frame_R)                             # UserList - Button
        self.Button_userlist.place(relx=0.52, rely=0.31, height=30, width=90)
        self.Button_userlist.configure(text="Who is here?")
        self.Button_userlist.configure(command=lambda: WhoIsHere())

        self.Frame_files = LabelFrame(self.Frame_R)                             # Send file - Frame
        self.Frame_files.place(relx=0.02, rely=0.38, relheight=0.18, relwidth=0.96)
        self.Frame_files.configure(text=' Send file:')

        self.Entry_file = Entry(self.Frame_files)                               # File path - Entry
        self.Entry_file.place(relx=0.04, rely=0.13, height=25, relwidth=0.57)

        self.Button_file = Button(self.Frame_files)                             # Select File - Button
        self.Button_file.place(relx=0.63, rely=0.13, height=26, relwidth=0.3)
        self.Button_file.configure(text='Select File')
        self.Button_file.configure(command=lambda: SelectFile())

        self.Button_opendir = Button(self.Frame_files)
        self.Button_opendir.place(relx=0.04, rely=0.55, height=26, relwidth=0.55)
        self.Button_opendir.configure(text='Received folder', command=lambda: os.system('start files'))

        self.Button_sendfile = Button(self.Frame_files)                         # Send File - Button
        self.Button_sendfile.place(relx=0.63, rely=0.55, height=26, relwidth=0.3)
        self.Button_sendfile.configure(text='Send File', command=lambda: threading.Thread(target= SendFile(self.Entry_file.get())))

        self.Label_nickname = Label(self.Frame_R)                               # Nick - Label
        self.Label_nickname.place(relx=0.03, rely=0.57, height=21, width=34)
        self.Label_nickname.configure(text='Nick:')

        self.Entry_nickname = Entry(self.Frame_R)                               # Nick - Entry
        self.Entry_nickname.place(relx=0.04, rely=0.61, height=27, relwidth=0.60)
        self.Entry_nickname.configure(background="white", font="TkFixedFont")
        self.Entry_nickname.insert(END, nickname)

        self.Button_nickname = Button(self.Frame_R)                             # Nick 'Go' - Button
        self.Button_nickname.place(relx=0.7, rely=0.61, height=27, relwidth=0.23)
        self.Button_nickname.configure(text='Go')
        self.Button_nickname.configure(command=lambda: Go_nickname())


        self.Label_key = Label(self.Frame_R)                                    # Key: - Label
        self.Label_key.place(relx=0.02, rely=0.66, height=24, width=34)
        self.Label_key.configure(text='Key:')

        self.Entry_key = Entry(self.Frame_R)                                    # Key - Entry
        self.Entry_key.place(relx=0.04, rely=0.70, height=27, relwidth=0.60)
        self.Entry_key.configure(background="white", font="TkFixedFont")
        self.Entry_key.insert(END, key)

        self.Button_key = Button(self.Frame_R)                                  # Key 'Go' - Button
        self.Button_key.place(relx=0.7, rely=0.70, height=27, relwidth=0.23)
        self.Button_key.configure(text='Go')
        self.Button_key.configure(command=lambda: ChangeKey(self.Entry_key.get()))

        self.Label_cleanlog = Label(self.Frame_R)                               # Log: - Label
        self.Label_cleanlog.place(relx=0.03, rely=0.75, height=24, width=34)
        self.Label_cleanlog.configure(text='Log:')

        self.Entry_log = Entry(self.Frame_R)                                    # Log - Entry
        self.Entry_log.place(relx=0.04, rely=0.79, height=30, relwidth=0.60)
        self.Entry_log.insert(END, log_file)

        self.Button_key = Button(self.Frame_R)                                  # Key 'set' - Button
        self.Button_key.place(relx=0.7, rely=0.79, height=28, relwidth=0.23)
        self.Button_key.configure(text='Set')
        self.Button_key.configure(command=lambda: ChangeLogfile(str(self.Entry_log.get())))

        self.Button_cleanlog = Button(self.Frame_R)                             # Log - 'Delete' - Button
        self.Button_cleanlog.place(relx=0.53, rely=0.85, height=28, width=97)
        self.Button_cleanlog.configure(text='Delete')
        self.Button_cleanlog.configure(command=lambda: CleanLog())

        self.Button_openlog = Button(self.Frame_R)                              # Log - 'Open' - Button
        self.Button_openlog.place(relx=0.03, rely=0.85, height=25, width=97)
        self.Button_openlog.configure(text='Open')
        self.Button_openlog.configure(command=lambda: OpenFile(log_file))

        self.Check_autorecv = Checkbutton(self.Frame_top, variable = chkbox)
        self.Check_autorecv.place(relx=0.006, rely=0.958)
        self.Check_autorecv.configure(text='Receive files: Disabled', onvalue=True, offvalue=False, command= lambda: UpdateCheckbox())

        self.Check_dataencrypt = Checkbutton(self.Frame_top, variable = chkbox2)
        self.Check_dataencrypt.place(relx=0.16, rely=0.958)
        self.Check_dataencrypt.configure(text='Data encryption: Enabled       Key: ' + key, onvalue=True, offvalue=False, command= lambda: UpdateCheckbox2())
        self.Check_dataencrypt.select()

        self.Message = Message(self.Frame_R)                                   # Credits Message
        self.Message.place(relx=0.04, rely=0.9, relheight=0.1, relwidth=0.93)
        self.Message.configure(width=210, justify='center' ,text="Python-based chat client\nCreated by:\nRon Benbenishti")

vp_start_gui()
