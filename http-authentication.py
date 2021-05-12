import socket
import time
import yaml
import re
import base64
import hashlib

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 3001))
server_socket.listen(5)
server_socket.setblocking(0)
sockets_array = []
complete_request_data = b''


def Do_auth():
    client_connection.sendall(
        b'HTTP/1.0 401 Unauthorized\nWWW-Authenticate: Basic realm="test"\r\n')
    complete_request_data = b''
    client_connection.close()


def send_response(host, response, decoded_complete_data):
    f = open(response, 'r')
    content = 0
    client_connection.sendall(
        b'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: 117\n\r\n')
    for l in f.readlines():
        content += len(l)
        response_data = str.encode(l)
        client_connection.sendall(response_data)
    f.close()
    if 'HTTP/1.0' in decoded_complete_data:
        if 'Connection: keep-alive' in decoded_complete_data:
            print("Connection: keep-alive")
        else:
            client_connection.close()


while True:
    response_file = ''
    header = re.compile("Authorization: (.*?)\n")
    time.sleep(1)
    try:
        for i in range(0, len(sockets_array)):
            try:
                request_data = sockets_array[i].recv(1024)
                complete_request_data += request_data
                decoded_complete_data = complete_request_data.decode()
                host = decoded_complete_data.splitlines()[1]
                try:
                    authheader = header.findall(decoded_complete_data)
                    authheader = authheader[0]
                    authheader = authheader[6:-1]
                except Exception as e:
                    pass
                with open('serverconfig.yaml') as data_file:
                    data = yaml.safe_load(data_file)
                    for v in data.values():
                        if v['name'] in host:
                            response_file = v['file']
                            username = v['username']
                            password = v['password']

                if response_file == '':
                    client_connection.sendall(
                        b'HTTP/1.1 404 NOT FOUND\nContent-Type: text/html\nContent-Length: 18\n\r\n<h1>Not Found</h1>')
                    complete_request_data = b''

                if '\r\n\r\n' in decoded_complete_data:
                    if(authheader):
                        authheader = base64.b64decode(authheader)
                        authheader = authheader.decode('utf-8')
                        authheaderUsername = authheader.split(':')[0]
                        authheaderPassword = authheader.split(':')[1]
                        authheaderPassword = bytes(authheaderPassword, 'utf-8')
                        authheaderPassword = hashlib.md5(authheaderPassword)
                        authheaderPassword = authheaderPassword.hexdigest()
                        if username == authheaderUsername and password == authheaderPassword:
                            send_response(host, response_file,
                                          decoded_complete_data)
                            complete_request_data = b''
                        else:
                            Do_auth()
                            complete_request_data = b''
                    else:
                        Do_auth()
            except Exception as e:
                pass
        client_connection, client_address = server_socket.accept()
        client_connection.setblocking(0)
        sockets_array.append(client_connection)
    except Exception as e:
        continue
