'''
天       若      有       情       天       亦       老
                  ;53GHH&&X835r.
               :18&HBBBBBMBBBBHX91:
             r&M#MMM###MHAHHABM#@@#&5.
            S##BBBMA951i,.,,,:is5XM##&;
           3#MBBBB5               1BM#H:
          5#MBBBBMG.               1BB#8
          AMBBBBBMH,                XM#8
          X#BBBBBMHS5sr:.    .,.... 9B@5
          ;BMBBBBBMM315rrhi59Shr;:i1&@H,
          ,BBBBBHMA8S1s9&HA85851;. hXGh
          .&MBBBH9;    S@s Si      si ,
           h#BBBB&hiir9HMi ,51si;i;; .
           .AMBBMB3r:hHAHAsri:;i;,.  .
            :AMBBM&HHAr::,     .;
             3#BBM5r#MH835sii;,
             ;#####h1H8r,...      .
            sA&5h3XM9G5:      .: .,
         :hX@Xi;   s3S95rshsshsi;,
     ,18&B##M:rA9ss;,:1si8@HX3;,8B&G31;,
 ,1SGB##MMBMS. 1M#&1sr:,sSSi    G#M###MHX3hi,
&B###MBBBBMM;   ,iii;i;rXG&X85. &MBBBBMM###MHX91;
#BBBBBBBM#B9r51   ;sssi3M@MM#Ar 8#BBBBBBBBBMM###B&
BBBBBBBM#Gi ;M&, ;;iir1r;5BMM:  sMBBBBBBBBBBBBBBMM
BBBBBMMA1 s .AM9SSABMM#9.rHMM5   &MBBBBBBBBBBBBBBB
BBBBBAH:  5; sM#BBHMBBB#GHMBMMS. 8#BBBBBBBBBBBBBBB
BBBBBM8   ,1:,1HG9h&MBMB#MMMMM#&3S#MMMBBMBMMMMMMMB
BBBBB#S    .;. ;G,.1AMBBBMMMBMM#M&BBBHBBBMBBHBMBBB
我       为       长       者       续       一       秒
前       排       膜       蛤，     不       出       bug
'''

from login import fuck_bilibili
import os
import time
import threading

def showIndex(flag):
    print("1.开始登陆")
    print("2.重设帐户")
    print("3.离开")
    if flag:
        print("4.每天签到")
        print("5.自动领瓜子")

if '__main__' == __name__:
    isLogin = 0
    isReSet = 0
    fuck = fuck_bilibili()
    fuck.init()
    print("初始化帐户成功!")
    while True:
        showIndex(isLogin)
        try:
            id = int(input("请输入: "))
            os.system("cls")
            if 1 == id:
                print("将会登陆 %s" % fuck.userid)
                fuck.Login(isReSet)
                isLogin = 1
            elif 2 == id:
                fuck.writeConfig(1)
                os.system("cls")
                print("重设帐户成功!")
                isReSet = 1
            elif 3 == id:
                print("再见 : )")
                time.sleep(1)
                os.system("cls")
                exit(0)

            if isLogin:
                if 4 == id:
                    thread = threading.Thread(target=fuck.Sign(), name='sign_thread')
                    thread.start()
                elif 5 == id:
                    pass
        except ValueError as e:
            print("%s\n请输入数字!" % e)
