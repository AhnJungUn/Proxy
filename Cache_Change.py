import os,ssl,sys,thread,socket
from hashlib import *
from OpenSSL import crypto
import traceback
from Func import *

cache_list = [".jpg",".jpeg",".png",".zip",".html"]
cache_list2 = ["jpg","jpeg","png","zip","html"]

def cache_change(request, s, conn, before, after): # s is None or wrap_socket

    fileExist = "false"

    temp, webserver, port = Parsing(request)

    """
    This routine is about extracting Filename by filtering several cases.
    But, i made new Filename for each requested file with hash_value(MD5) of requested url. 
    
    cnt = temp.count("/")

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in temp.split("/")[i]):
                filename = temp.split("/")[i]
                break

    cnt = filename.count("%2F")

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in filename.split("%2F")[i]):
                filename = filename.split("%2F")[i]
                break

    cnt = filename.count("&") 

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in filename.split("&")[i]):
                filename = filename.split("&")[i]
                break
            
    cnt = filename.count("%26")        

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in filename.split("%26")[i]):
                filename = filename.split("%26")[i]
                break

    cnt = filename.count("?")        

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in filename.split("?")[i]):
                filename = filename.split("?")[i]
                break

    cnt = filename.count("%3F")        

    for i in range(cnt+1):
        for j in range(len(cache_list)):
            if(cache_list[j] in filename.split("%3F")[i]):
                filename = filename.split("%3F")[i]
                break               
    """

    filename = md5(temp).hexdigest()

    try:

        if(request.find("no-cache") != -1 or request.find("no-store") != -1 or request.find("must-revalidate") != -1): # HTTP/1.1 Cache-Control

            if(s == None):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                s.connect((webserver, port))
                s.send(request)         

            else: # s is wraped socket with ssl
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

        else:
            f = open("C:/Python27/"+filename, "r")
            output = f.read()
            fileExist = "true"
            OUTPUT = "HTTP/1.1 200 OK" + "\r\n" + "Content-Length: " + str(len(output)) + "\r\n\r\n" + output
            conn.send(OUTPUT)
            print "filename : ",filename
            print "cache success"

    except IOError: 
        if(fileExist == "false"):

            try:
                if(s == None):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                    s.connect((webserver, port))
                    s.send(request)
                else:
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

                if(data.find("chunked") != -1): 
                    data = Chunk_Recv(s, data)

                if(data.find("no-cache") == -1 and data.find("no-store") == -1 and data.find("must-revalidate") == -1):

                    pos = data.find("\r\n\r\n")
                    file_content = data[pos+4:]
                    tmpFile = open("C:/Python27/"+filename,"wb")
                    tmpFile.write(file_content)
                        
                if(data.find("Content-Length: ") != -1):
                    data = Content_Change(data, before, after)

                if(data.find("chunked") != -1):
                    data = Chunk_Change(data, before, after)

                data = data.replace(before, after)
                conn.send(data)

                                  
            except socket.error, (value, message):
                if s:
                    s.close()
                if conn:
                    conn.close()
                sys.exit(1)
        else: 
            print "File Not Found"
