'''
Utility functions to support socket communication.
'''
from socket import timeout as SocketTimeoutError

def send_and_receive(sock, command):
    ''' Send command and get return '''
    try:
        sock.send(command.encode())
        ret = sock.recv(1024).decode()
        while ret.find(',EndOfAPI') == -1:
            ret += sock.recv(1024).decode()
    except SocketTimeoutError:
        return [-2, '']
    except OSError as err:
        print('Socket error : ' + err)
        return [-2, '']

    for i, value in enumerate(ret):
        if value == ',':
            return [int(ret[0:i]), ret[i+1:-9]]
