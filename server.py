#!/usr/bin/python

from socket import *
from datetime import datetime
from time import *
from thread import *
import sys, os, select, Queue, argparse, random
try:
    os.stat('files')
except:
    os.mkdir('files')
ip, port, buffer  = '', 0, 0

def GetIP():
    ip = gethostbyname(gethostname())
    if '127.' in ip:
        ip = ([l for l in ([ip for ip in gethostbyname_ex(gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket()]][0][1]]) if l][0][0])
    return ip

def GetMOTD(buff):
    if os.path.isfile('motd.txt') == False:
        file = open('motd.txt','w')
        file.write('Welcome to my server')
        file.close()
    file = open('motd.txt','r')
    MOTD = file.read()
    file.close()
    return MOTD

def TimeStamps():
    return datetime.fromtimestamp(time()).strftime('(%H:%M:%S)')

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, help='Set the server IP', required=False, default=GetIP())
parser.add_argument('--port', type=int, help='Set the listener port', required=False, default=7000)
parser.add_argument('--buffer', type=int, help='Set the Buffer', required=False, default=1024)
args = parser.parse_args()

ip = args.ip
port = args.port
buffer = args.buffer
MOTD = GetMOTD(buffer)

server = socket()
try:
    server.bind((ip, port))
except:
    print '>> Binding Error #9543: IP or PORT is not available for use'
    quit()
server.listen(5)
server.settimeout(10)
output = []
message_queues = {}
list_of_clients = [server]

print '>> Server has been started'
print 'IP:',ip
print 'Port:',port
print 'Buffer:',buffer
print 'Message Of The Day:\n' + MOTD

def Broadcast(data, client):
    global sender
    message_queues[client].put(data)
    sender = client
    if client not in output:
        output.append(client)


def TransferFile(file_data, size, conn):
    for i in range(0,file_size,buffer):
        Broadcast()
    footer = conn.recv(buffer)
    if 'END_FILE' in footer:
        print '>> File transferring process success'
    else:
        print '>> Error exception: #1377'
try:
    while list_of_clients:
        sleep(0.01)
        readable, writable, exceptional = select.select(list_of_clients, output, list_of_clients)
        for client in readable:
            if client is server:
                conn, addr = server.accept()
                conn.send(str(buffer) + '#MOTD#' + MOTD)
                list_of_clients.append(conn)
                conn.setblocking(1)
                message_queues[conn] = Queue.Queue()

            else:
                try:
                    message = client.recv(buffer)
                    if '#PING#' in message:
                        print '>> Ping has received from ' + addr[0] + ':' + str(addr[1])
                        print '>> Sending pong'
                        conn.send('PONG')

                    elif '#IDENT#' in message:
                        con_nickname = message.split('# #')[0]
                        con_ip = message.split('# #')[2]
                        con_buffer = message.split('# #')[3].strip(' ')
                        print '>> Connection identify:\n>>      Nickname:',con_nickname,'Host IP:',con_ip,'Buffer:',con_buffer
                        if int(con_buffer) != buffer:
                            print '>> Warnning: Buffers are not match\nServer buffer:',buffer,'\nClient buffer:',con_buffer

                    elif 'INCOMING_FILE' in message:
                        print '\n>> File transfer has recognized:'
                        FULLDATA = ''
                        file_details = message.split('# #')
                        file_size = int(file_details[1])
                        if len(str(file_size)) < 7:
                            file_size_kb = str("%.2f" % float(int(file_size) * 0.001)) + 'KB'
                        elif len(str(file_size)) > 6:
                            file_size_kb = str("%.2f" % (int(file_size) * 0.000001)) + 'MB'
                        else:
                            pass
                        file_sender = file_details[2] + ' (' + file_details[3] + ')'
                        file_name = file_details[4]
                        file_buffer = int(file_details[5])
                        print '>>>>   File name : ' + file_name
                        print '>>>>   File size : ' + file_size_kb
                        print '>>>>   Sent by   : ' + file_sender + '\n'
                        Broadcast(message, client)
                        try:
                            conn.send('START FILE TRANSFER# #' + str(file_size))
                            for buff in range(0, file_size, file_buffer):
                                file_data = conn.recv(buffer)
                                FULLDATA += file_data

                        except Exception as reason:
                            print '>> Error #4366: ', str(reason)

                    elif 'END_FILE' in message:
                        f_name = ''.join(file_name.split('.')[0:-1]) + '_'
                        f_ext = '.' + ''.join(file_name.split('.')[-1])
                        for i in range(3):
                            f_name += str(random.randint(0,9))
                        file_name = f_name + f_ext
                        save_file = open('Files\\' + file_name, 'wb')
                        save_file.write(FULLDATA)
                        save_file.close()
                        recv_file = int(os.path.getsize('Files\\' + file_name))
                        try:
                            if recv_file == 0:
                                print '>> Unexpected Error: #8432:', file_name, 'is empty.'
                            elif recv_file == file_size:
                                print '>> File transferring process complete'
                                print '>> File has been saved in: ' + os.getcwd() + '\\Files\\' + file_name
                                # TransferFile(FULLDATA, file_size, conn)       # Broadcast to all clients
                            else:
                                print '>> Unexpected Error: #9921'
                        except Exception as reason:
                            print '>> Error #1471: ' + str(reason)

                    elif '#EXIT#' in message:
                        list_of_clients.remove(client)
                        client.close()

                    elif message:
                        print TimeStamps() + " (" + addr[0] + " / " + str(len(list_of_clients)-1) + "): " + message
                        Broadcast(message, client)


                    else:
                        if client in output:
                            output.remove(client)
                        # list_of_clients.remove(client)
                        # client.close()
                        # del message_queues[client]

                except Exception as reason:
                    print 'Error #3433: ', str(reason)
                    list_of_clients.remove(client)
                    conn.close()

        for client in writable:
            try:
                next_msg = message_queues[client].get_nowait()
            except Queue.Empty:
                output.remove(client)
            except Exception as reason:
                print str(reason)

            for client in list_of_clients:
                try:
                    if client != server and client != sender:
                        client.send(next_msg)
                except Exception as reason:
                    print '>> Error #2355: ' + str(reason)
            if client in output:
                output.remove(client)




        for client in exceptional:
            list_of_clients.remove(client)
            if client in output:
                output.remove(client)
            client.close
            del message_queues[client]

except KeyboardInterrupt:
    sys.quit()

except Exception as reason:
    pass
    # print '>> Error #9941 : ' + str(reason)
