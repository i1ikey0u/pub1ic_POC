Microsoft Outlook WebAPP Brute
==========

Outlook_BP.py单线程.   Outlook_mut_threa_bp.py是多线程，需要指定线程数。

多线程版本在SSL handshake时可能出错，比如破解email.baidu.com时。这跟服务器的稳定性有关。 目前的处理方法是出错后重试!


使用:
Outlook_BP.py domain usersfile passwdfile
or
Outlook_mut_threa_bp.py domain usersfile passwdfile  theradnum
domain是站点域名，不需要https前缀
users和passwords是字典文件的名称。
