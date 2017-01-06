import requests
import json
import time
import os
from PIL import Image
import rsa
import binascii
from bs4 import BeautifulSoup

class fuck_bilibili():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Connection' : 'keep-alive',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        self.userid = ''
        self.pwd = ''
        self.postdata = {}
        self.errorSum = 10
        self.userName = ''

    def init(self):
        self.readConfig()

        url = 'https://passport.bilibili.com/login'
        try:
            self.session.get(url)
            self.errorSum = 10
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not connect '%s', will try again..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\ncan not connect '%s', please try again manually!" % url)
                exit(1)

    def rsaEncrypt(self):
        url = 'http://passport.bilibili.com/login?act=getkey'
        try:
            getKeyResponse = self.session.get(url)
            self.errorSum = 10
            token = json.loads(getKeyResponse.content.decode('utf-8'))
            self.pwd = str(token['hash']+self.pwd).encode('utf-8')
            key = token['key']
            key = rsa.PublicKey.load_pkcs1_openssl_pem(key)
            self.pwd = rsa.encrypt(self.pwd, key)
            self.pwd = binascii.b2a_base64(self.pwd)
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not connect '%s', will try again..." % (e, url))
                time.sleep(1)
                return self.rsaEncrypt()
            else:
                print("\ncan not connect '%s', please try again manually!" % url)
                exit(1)
        except json.JSONDecodeError as e:
            print("%scan not load key, please check manually!")
            exit(1)

    def readConfig(self):
        try:
            with open("config.json", "r") as f:
                config = json.loads(f.read())
                self.userid = config["userid"]
                self.pwd = config["pwd"]
        except IOError as e:
            print("%s\ncan not open 'config.json', will write 'config.json'..." % e)
            return self.writeConfig()
        except json.JSONDecodeError as e:
            print("%s\n'config.json' was broken, will rewrite 'config.json'..." % e)
            return self.writeConfig()
        except KeyError as e:
            print("can not get %s" % e)
            return self.writeConfig()

    def writeConfig(self, arg = 0):
        if arg:
            self.userid = ''
            self.pwd = ''

        if '' == self.userid:
            self.userid = input("please input your account: ")
        if '' == self.pwd:
            self.pwd = input("please input your password: ")

        config = {
            "userid" : self.userid,
            "pwd" : self.pwd
        }

        try:
            with open("config.json", "w") as f:
                f.write(json.dumps(config))
        except IOError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not save 'config.json', will try again...")
                time.sleep(1)
                return self.writeConfig()
            else:
                print("\ncan not save 'config.json', please try again manually!")
                exit(1)

        self.errorSum = 10

    def getVerCode(self):
        url = 'https://passport.bilibili.com/captcha'
        try:
            verCodeResponses = self.session.get(url)
            self.errorSum = 10
            with open('verCode.jpg', 'wb') as f:
                f.write(verCodeResponses.content)
            self.errorSum = 10
            im = Image.open('verCode.jpg')
            im.show()
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not connect '%s', will try again..." % (e, url))
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\ncan not connect '%s', please try again manually!" % url)
                exit(1)
        except IOError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not save 'varImage.jpg', will try again..." % e)
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\ncan not save 'varImage.jpg', please try again manually!")
                exit(1)
        except OSError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not open 'varImage.jpg'" % e)
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\ncan not can not open 'varImage.jpg', please try again manually!")
                exit(1)

        return input("please input verify code (press '0' to refresh): ")

    def login(self):
        code = '0'

        while '0' == code:
            code = self.getVerCode()

        self.rsaEncrypt()

        url = 'https://passport.bilibili.com/login/dologin'
        data = {
            'act': 'login',
            'gourl': '',
            'keeptime': '2592000',
            'userid': self.userid,
            'pwd': self.pwd,
            'vdcode': code
        }

        try:
            loginResponse = self.session.post(url, data=data)
            soup = BeautifulSoup(loginResponse.content, 'lxml')
            s = str(soup.select('center')[0])
            s = s.replace('\n', '')
            s = s.replace('\r', '')
            s = s.replace(' ', '')
            s = s.split('>')
            s = s[2]
            s = s.replace('<br/', '')
            print("login error: %s" % s)
            return False
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not connect '%s', will try again..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\ncan not connect '%s', please try again manually!" % url)
                exit(1)
        except:
            print("login success!")
            return True

    def getAccountName(self):
        url = 'https://account.bilibili.com/home/userInfo'

        try:
            accountNameResponse = self.session.get(url)
            soup = BeautifulSoup(accountNameResponse.content, 'lxml')
            s = str(soup)
            s = s.replace('<html><body><p>', '')
            s = s.replace('</p></body></html>', '')
            s = s.replace('\n', '')
            s = s.replace('\r', '')
            s = s.replace(' ', '')
            s = s.replace('\t', '')
            self.userName = json.loads(s)['data']['uname']
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\ncan not connect '%s', will try again..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\ncan not connect '%s', please try again manually!" % url)
                exit(1)
        except json.JSONDecodeError as e:
            print("%scan not load data, please check manually!")
            exit(1)

    def Login(self):
        if self.login():
            self.getAccountName()
            print("welcome %s!" % self.userName)
        else:
            return self.Login()

def showIndex():
    print("1.start")
    print("2.reset account")
    print("3.quit")

if '__main__' == __name__:
    fuck = fuck_bilibili()
    fuck.init()
    print("init account success")
    while True:
        showIndex()
        try:
            id = int(input("please input your choise: "))
            os.system("cls")
            if 1 == id:
                print("will login %s" % fuck.userid)
                fuck.Login()
            elif 2 == id:
                fuck.writeConfig(1)
                os.system("cls")
                print("reset account success")
            elif 3 == id:
                print("bye!")
                time.sleep(1)
                os.system("cls")
                exit(0)
        except ValueError as e:
            print("%s\nplease enter digit!" % e)
