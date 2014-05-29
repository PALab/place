"""
Simple single-thread server that listens for connections on a
certain port, then triggers the scope when a certain character is
received.  The data from the scope are downloaded, plotted, and saved.

Example client:

import socket
host = 'localhost'    # The remote host
port = 99999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('t') # trigger command
s.close()

"""

import socket
import threading
import time
import tds3014b
import datetime

listen_port = 99999
scope_address = '192.168.0.5'

def main():
    # Setup scope
    tds = tds3014b.tds3014b(scope_address)
    # Make sure there's a scope there.
    try:
        idn = tds.get_idn()
    except IOError:
        print "Couldn't communicate with scope at %s" % scope_address
        return
    else:
        print "Found scope at %s: %s" % (scope_address, idn)
    
    # Setup network
    host = '' # all interfaces
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, listen_port))
    s.listen(1) # allow backlog of 1 other connection

    keepgoing = True
    
    def serve():
        while(keepgoing):
            print 'Waiting for connection.'
            conn, addr = s.accept()
            print 'Connected to:', addr
            while True:
                try:
                    data = conn.recv(1024) # blocking
                except socket.error:
                    break
                if(data == ''):
                    break # disconnected client

                for char in data:
                    # Take conditional action
                    print "[%s] Cmd: %s" % (char, str(datetime.datetime.now()))
                    if(char == 't'):
                        conn.send('Triggering scope\r\n')
                        # Trigger the scope
                        tds.force_trig()
                        header, data = tds.get_waveform(channel=1, plot=True)
                        header, data = tds.get_waveform(channel=2, plot=True)
                    elif(char == 'q'):
                        # quit
                        conn.send('Server exiting\r\n')
                        conn.close()
                        return
            conn.close()
            print 'Closed connection.'

    t = threading.Thread(target=serve)
    t.start()

#    time.sleep(10)
#    keepgoing = False
#    print "time out"

if __name__ == '__main__':
    main()
