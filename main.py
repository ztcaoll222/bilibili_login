from login import fuck_bilibili
import os
import time

def showIndex():
    print("1.开始登陆")
    print("2.重设帐户")
    print("3.离开")

if '__main__' == __name__:
    fuck = fuck_bilibili()
    fuck.init()
    print("初始化帐户成功!")
    while True:
        showIndex()
        try:
            id = int(input("请输入: "))
            os.system("cls")
            if 1 == id:
                print("将会登陆 %s" % fuck.userid)
                fuck.Login()
            elif 2 == id:
                fuck.writeConfig(1)
                os.system("cls")
                print("重设帐户成功!")
            elif 3 == id:
                print("再见 : )")
                time.sleep(1)
                os.system("cls")
                exit(0)
        except ValueError as e:
            print("%s\n请输入数字!" % e)
