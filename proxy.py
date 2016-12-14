import os,ssl,sys,thread,socket
from hashlib import *
from OpenSSL import crypto
import traceback
from Func import *
from Cache_Change import *

BACKLOG = 50           
MAX_DATA_RECV = 999999  
DEBUG = True            
cache_list = [".jpg",".jpeg",".png",".zip",".html"]
cache_list2 = ["jpg","jpeg","png","zip","html"]

def main():

    if (len(sys.argv)<2):
        print "No port given, using :8080 (http-alt)" 
        port = 8080
    else:
        port = int(sys.argv[1]) 

    host = '127.0.0.1'               
    
    print "Proxy Server Running on ",host,":",port

    if(len(sys.argv) == 4):
        before = sys.argv[2] # want to be changed
        after = sys.argv[3] # want to change with

    if(len(sys.argv) == 2):
        before = ""
        after = ""
        
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)
    
    except socket.error, (value, message):
        if s:
            s.close()
        print "Could not open socket:", message
        sys.exit(1)

    while 1:
        conn, client_addr = s.accept()
        thread.start_new_thread(proxy_thread, (conn, client_addr, before, after))
        
    s.close()


def proxy_thread(conn, client_addr, before, after):

    sock = None
    
    request = conn.recv(MAX_DATA_RECV)

    while(request.find("\r\n\r\n") == -1):
                newdata = conn.recv(MAX_DATA_RECV)    
                request = request + newdata 

    if(request.find("Content-Length: ") != -1):
        request = Content_Recv(conn, request)

    if(request.find("gzip") != -1):
        request = request.replace("gzip","")
    
    temp, webserver, port = Parsing(request)
    
    if(request.find("CONNECT") != -1): # https connection

        pos = request.find("CONNECT")
        content_1 = request[pos:]
        info = content_1.split(" ")[1]
        HOST = info.split(":")[0]
        PORT = int(info.split(":")[1])

        try:
            server_key, server_cert = cert_gen(HOST, 'root.crt', 'root.key')

            conn.send("HTTP/1.1 200 Connection Established\r\n\r\n")
                
            client_sock = ssl.wrap_socket(conn, server_side = True, certfile = server_cert, keyfile = server_key)
                
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            server_sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)
                                            
            while(1):

                request = client_sock.recv(MAX_DATA_RECV)

                while(request.find("\r\n\r\n") == -1):
                    newdata = client_sock.recv(MAX_DATA_RECV)    
                    request = request + newdata 

                if(request.find("Content-Length: ") != -1):
                    request = Content_Recv(client_sock, request)

                if(request.find("gzip") != -1):
                    request = request.replace("gzip","")

                temp, webserver, port = Parsing(request)

                result = 0

                for i in range(len(cache_list)):
                    if(cache_list[i] in temp):
                        result = 1

                if(result == 1): # cache and data_change
                    cache_change(request, server_sock, client_sock, before, after)
                    
                else: # just data_change

                    server_sock.send(request)
                        
                    newdata = server_sock.recv(MAX_DATA_RECV)

                    while(newdata.find("HTTP/1.1 200 OK") == -1):
                        client_sock.send(newdata)
                        newdata = server_sock.recv(MAX_DATA_RECV)
                        
                    data = newdata
                            
                    while(data.find("Content-Length") == -1 and data.find("chunked") == -1): 
                        newdata = server_sock.recv(MAX_DATA_RECV)
                        data = data + newdata
                        
                    while(data.find("\r\n\r\n") == -1):
                        newdata = server_sock.recv(MAX_DATA_RECV)    
                        data = data + newdata              
                        
                    if(data.find("Content-Length: ") != -1):
                        data = Content_Recv(server_sock, data)
                        data = Content_Change(data, before, after)
                    

                    if(data.find("chunked") != -1):    
                        data = Chunk_Recv(server_sock, data)
                        data = Chunk_Change(data, before, after)
                                                   
                    data = data.replace(before, after)
                    client_sock.write(data)
                    print "Good"
                                
            sock.close()
            conn.close()
                        
                         
        except socket.error, (value, message):
            if sock:
                sock.close()
                print traceback.print_exc()
            if conn:
                conn.close()
                print traceback.print_exc()
        
            sys.exit(1)
                
    else: 

        result = 0

        for i in range(len(cache_list)):
            if(cache_list[i] in temp):
                result = 1

        if(result == 1): # cache and data_change

            cache_change(request, None, conn, before, after)

        else: # just data_change
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                s.connect((webserver, port))
                s.send(request)         
                
                newdata = s.recv(MAX_DATA_RECV)

                while(newdata.find("HTTP/1.1 200 OK") == -1):
                    conn.send(newdata)
                    newdata = s.recv(MAX_DATA_RECV)

                data = newdata
                        
                while(data.find("Content-Length") == -1 and data.find("chunked") == -1): 
                    newdata = s.recv(MAX_DATA_RECV)
                    data = data + newdata

                while(data.find("\r\n\r\n") == -1):
                    newdata = s.recv(MAX_DATA_RECV)    
                    data = data + newdata              

                if(data.find("Content-Length: ") != -1):
                    data = Content_Recv(s, data)
                    data = Content_Change(data, before, after)

                if(data.find("chunked") != -1):     
                    data = Chunk_Recv(s, data)
                    data = Chunk_Change(data, before, after)

                data = data.replace(before, after)
                conn.send(data)

                s.close()
                conn.close()

            except socket.error, (value, message):
                if s:
                    s.close()
                if conn:
                    conn.close()
                sys.exit(1)
            
    
if __name__ == '__main__':
    main()
