import os,sys,socket
from hashlib import sha256
from OpenSSL import crypto
MAX_DATA_RECV = 999999

def cert_gen(domain, ca_crt, ca_key): 

    domain_hash = sha256(domain.encode()).hexdigest()
    key_path = os.path.join("C:\Certificates", domain+".key")
    cert_path = os.path.join("C:\Certificates", domain+".crt")

    if os.path.exists(key_path) and os.path.exists(cert_path):
        pass

    else:
        serial = int(domain_hash, 36)

        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(ca_crt).read())
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(ca_key).read())

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        cert = crypto.X509()
        cert.get_subject().C = "IN"
        cert.get_subject().ST = "AP"
        cert.get_subject().L = domain
        cert.get_subject().O = "AhnJungUn"
        cert.get_subject().OU = "Inbound-Proxy"
        cert.get_subject().CN = domain 
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)
        cert.set_serial_number(serial)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(ca_key, "sha256")

        domain_key = open(key_path,"wb")
        domain_key.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        domain_key.close()
        
        domain_cert = open(cert_path,"wb")
        domain_cert.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        domain_cert.close()

    return key_path, cert_path


def Parsing(request):

    first_line = request.split('\r\n')[0]
    
    url = first_line.split(' ')[1]
    http_pos = url.find("://")          

    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]       

    port_pos = temp.find(":")           
    
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1

    if (port_pos==-1 or webserver_pos < port_pos):  # default port
        port = 80
        webserver = temp[:webserver_pos]

    else:                                           # specific port
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    return temp, webserver, port


    
def Content_Recv(s,data): 
    
    POS_1 = data.find("Content-Length: ")
    content_length = data[POS_1+16:]
    
    POS_2 = content_length.find("\r\n")
    content_length = content_length[:POS_2]
    content_len = int(content_length)
        
    header = data.split("\r\n\r\n")[0]
    header_len = len(header) + 4
    total_len = header_len + content_len

    while(len(data) != total_len):
        new_data = s.recv(MAX_DATA_RECV)
        data = data + new_data

    return data


def Chunk_Recv(s,data):

    while(data[-5:] != "0\r\n\r\n"):
        new_data = s.recv(MAX_DATA_RECV)
        data = data + new_data

    return data



def Content_Change(data, before, after):

    if(before == "" and after == ""):
        return data

    else:
        diff = len(before) - len(after)
        cnt = data.count(before)
        POS_1 = data.find("Content-Length: ")
        First = data[:POS_1+16]
        Middle = data[POS_1+16:]
        POS_2 = Middle.find("\r\n")
        Last = Middle[POS_2:]
        Middle = Middle[:POS_2]
        Middle = str(int(Middle)-(diff*cnt))

        data = First + Middle + Last

        return data

def Chunk_Change(data, before, after):

    if(before == "" and after == ""):
        return data

    else:
        
        diff = len(before) - len(after)
        
        POS_1 = data.find("\r\n\r\n")
        header = data[:POS_1+4]  
        body = data[POS_1+4:]
        POS_2 = body.find("\r\n")
        title = body[:POS_2]

        title_len = len(title)
        content_len = int(title,16)
        content = body[(POS_2+2):(title_len + content_len + 4)] 
        res = body[(title_len + content_len + 4):]

        cnt = content.count(before)
        content_len = content_len - diff*cnt
        title = str(hex(content_len))[2:]
        DATA = header + title + "\r\n" + content

        if(res.split("\r\n")[0] != ""):
            res_value=int(res.split("\r\n")[0],16)
        else:
            res_value = 0
        
        while(res_value != 0):
            POS = res.find("\r\n")
            title = res[:POS]
            title_len = len(title)
            content_len = int(title,16)
            content = res[(POS+2):(title_len + content_len + 4)] 
            res = res[(title_len+content_len+4):]
            cnt = content.count(before)
            content_len = content_len - diff*cnt
            title = str(hex(content_len))[2:]                    
            DATA = DATA + title + "\r\n" + content
            if(res.split("\r\n")[0] != ""):
                res_value=int(res.split("\r\n")[0],16)
            else:
                break
            
        DATA = DATA + res 
        data = DATA

        return data
