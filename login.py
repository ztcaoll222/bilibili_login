import requests
import json
import time
from PIL import Image
import rsa
import binascii
from bs4 import BeautifulSoup
import pickle

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
        url = 'https://passport.bilibili.com/login'
        try:
            self.session.get(url)
            self.errorSum = 10
        except requests.exceptions.ConnectionError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\n无法连接 '%s', 重试..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\n无法连接 '%s'， 超过重试次数， 请手动重试!" % url)
                exit(1)

        self.readConfig()

    def readConfig(self):
        filename = 'config.json'
        try:
            with open(filename, "r") as f:
                config = json.loads(f.read())
                self.userid = config["userid"]
                self.pwd = config["pwd"]
        except IOError as e:
            print("%s\n无法打开 '%s', 将会创建 '%s'..." % (e, filename, filename))
            return self.writeConfig()
        except json.JSONDecodeError as e:
            print("%s\n'%s' 遭到破坏, 将会重写 '%s'..." % (e, filename, filename))
            return self.writeConfig()
        except KeyError as e:
            print("无法获得 %s" % e)
            return self.writeConfig()

    def writeConfig(self, arg = 0):
        if arg:
            self.userid = ''
            self.pwd = ''

        if '' == self.userid:
            self.userid = input("请输入用户名: ")
        if '' == self.pwd:
            self.pwd = input("请输入密码: ")

        config = {
            "userid" : self.userid,
            "pwd" : self.pwd
        }

        filename = 'config.json'
        try:
            with open(filename, "w") as f:
                f.write(json.dumps(config))
        except IOError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\n无法保存 '%s', 重试..." % (e, filename))
                time.sleep(1)
                return self.writeConfig()
            else:
                print("\n无法保存 '%s', 超过重试次数，请手动重试!" % filename)
                exit(1)

        self.errorSum = 10

    def loadCookies(self):
        filename = "%s.cookies" % self.userid
        try:
            with open(filename) as f:
                self.session.cookies = requests.utils.cookiejar_from_dict(pickle.loads(f))
        except IOError as e:
            print("%s\n无法加载 '%s', 将重新保存 '%s'..." % (e, filename, filename))

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
                print("%s\n无法连接 '%s', ..." % (e, url))
                time.sleep(1)
                return self.rsaEncrypt()
            else:
                print("\n无法连接 '%s', 超过重试次数, 请手动重试!" % url)
                exit(1)
        except json.JSONDecodeError as e:
            print("%s无法加载token, 请手动检查!")
            exit(1)

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
                print("%s\n无法连接 '%s', 重试..." % (e, url))
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\n无法连接 '%s', 超过重试次数, 请手动重试!" % url)
                exit(1)
        except IOError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\n无法保存 'varImage.jpg', 重试..." % e)
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\n无法保存 'varImage.jpg', 超过重试次数, 请手动重试!")
                exit(1)
        except OSError as e:
            self.errorSum -= 1
            if self.errorSum:
                print("%s\n无法打开 'varImage.jpg'" % e)
                time.sleep(1)
                return self.getVerCode()
            else:
                print("\n无法打开 'varImage.jpg', 超过重试次数, 请手动重试!")
                exit(1)

        return input("请输入验证码 (按 '0' 刷新): ")

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
                print("%s\n无法连接 '%s', 重试..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\n无法连接 '%s', 超过重试次数, 请手动重试!" % url)
                exit(1)
        except:
            print("登陆成功!")
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
                print("%s\n无法连接 '%s', 重试..." % (e, url))
                time.sleep(1)
                return self.init()
            else:
                print("\n无法连接 '%s', 超过重试次数, 请手动重试!" % url)
                exit(1)
        except json.JSONDecodeError as e:
            print("%s无法加载用户信息, 请手动检查!")
            exit(1)

    def saveCooktes(self):
        pass

    def Login(self):
        if self.login():
            self.getAccountName()
            print("欢迎 %s!" % self.userName)
        else:
            return self.Login()
