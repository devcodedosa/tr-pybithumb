# -*- coding: utf-8 -*-
from pybit_logger import *
from telegram_send import send_message
import sys
from time import sleep
import datetime
import os
import traceback
import python_bithumb
from websocket import *
import psutil
import signal


access_key = "내 빗썸 API Access Key"
secret_key = "내 빗썸 Secret Key"


bithumb = python_bithumb.Bithumb(access_key, secret_key)

# 로그 시작
log = botLogger()

# PID 이름 설정
pid_file = 'trCoinBithumb.pid'

class trCoinBit:
    def __init__(self):

        self.parent_pid = os.getpid()

        signal.signal(signal.SIGCHLD, handle_sigchld)
        
        # 코인 리스트
        self.tr_coin_list = 'KRW-BTC'
        
        # 원화 잔고 리스트
        self.my_krw = {}
        
        # 원화 잔고를 얻어온다. 
        self.getAccBalance()
        
        log.debug("trCoinBit시작")
        
        
    def getAccBalance(self):
        # 계좌 잔고 조회
        r = bithumb.get_balances()
        
        r_balances = [] # 리스트 안에 딕셔너리 구조임
  
        # krw_balance : 보유중인 원화 잔고
        # avilable_krw : 매수 가능한 원화 잔고
        # coin_balance : 보유중인 코인 잔고
        # avg_buy_price : 보유중인 코인 매수 평단가
        # profit : 보유중인 코인 수익률
        # coin_type : 보유중인 코인 타입
        # coin_amount : 코인 총 평가금액
        

        fee = 0.05  # 거래 수수료
        # 자료형은 딕셔너리이다.
        try:
            #i = 0
            for i in range(len(r)):
                # 현재 원화 잔고 얻어오기
                r_balance = {'coin_type': 'NONE', 'coin_balance' : 0, 'avg_buy_price': 0, 'profit': 0, 'coin_amount':0 }
                
                money =  float(r[i]['balance'])                     
                
                if r[i]['currency'] == 'KRW':
                    print("현재 잔고는 원화로 %f 원 입나다." % money)
                    
                    money =  float(r[i]['balance'])
                    self.my_krw['krw_balance'] = money

                    # 매수 가능 금액 계산
                    if money > 0: # 잔고가 있을때
                        v = money * fee 
                        self.my_krw['avilable_krw'] = money - v
                        print("매수 가능 금액 : %f" % self.my_krw['avilable_krw'])
                    else:
                        self.my_krw['avilable_krw'] = 0
                        print("매수 가능한 잔고가 없습니다.")
                        
                        
                else:  # 코인을 보유할시
                    # 현재 보유중인 코인 타입 얻어오기
                    get_coin_type = 'KRW-' + r[i]['currency']                
                    r_balance['coin_type'] = get_coin_type
                    
                    print("현재 보유중인 코인 타입은 %s 입니다." % r_balance['coin_type'])   
                        
                    get_coin = float(r[i]['balance'])
                    if get_coin > 0: 
                        print("현재 보유중인 코인은 %0.15f 입니다." % get_coin)
                        r_balance['coin_balance'] = get_coin
                    else:
                        print("코인이 없습니다.")
                        r_balance['coin_balance'] = 0
                        
                    # 코인 평단가 얻어오기
                    avg_buy_price = float(r[i]['avg_buy_price'])
                    if avg_buy_price > 0:
                        print("현재 보유중인 코인의 평균 단가는 %f 입니다" % avg_buy_price)
                        r_balance['avg_buy_price'] = avg_buy_price
                    else:
                        r_balance['avg_buy_price'] = 0
                    
                    # 코인 평가 금액 계산
                    coin_amount = avg_buy_price * get_coin
                    
                    print("현재 코인의 총 매수금액은 : %f 입니다." % coin_amount)
                    r_balance['coin_amount'] = coin_amount
                    
                
                    # 코인 수익률 계산
                    sleep(0.05)     # 현재가 얻어오기 에러 발생으로 인한 딜레이 추가
                    if avg_buy_price > 0: # 잔고가 있을 경우
                        now_price = self.getNowPrice(get_coin_type)
                        #profit = ((now_price/(1+fee)) / (avg_buy_price * (1+fee))) - 1
                        profit = ((now_price / avg_buy_price) - 1) * 100
                        print("현재 보유중인 코인의 수익률은 %f 입니다. 현재가:%d, 보유가:%f" % (profit, now_price, avg_buy_price))
                        r_balance['profit'] = profit
                    else:
                        r_balance['profit'] = 0
                        
                    if r_balance['coin_balance'] > 0:  # 코인이 있다면 True 
                        self.buy_flag = True
                    else:
                        self.buy_flag = False
                    
                
                    r_balances.append(r_balance)
                    
                    print("--------------------------------------------------")
                #r_balances.append(r_balance)
                
            if r_balances[0]['coin_type'] != 'NONE':
                print("현재 코인 1개 이상 보유중")
                self.buy_flag = True
            else:
                self.buy_flag = False

        except:
            #err = traceback.format_exc()
            #print(err)
            print("계좌 잔고 값 얻어오기에서 에러가 발생했습니다.")
            log.debug("계좌 잔고 값 얻어오기에서 에러가 발생했습니다.")
            r_balance = {'krw_balance': 0, 'coin_balance' : 0, 'avg_buy_price': 0, 'avilable_krw': 0, 'profit': 0, 'coin_type': 'NONE', 'coin_amount':0}
            self.my_krw['krw_balance'] = 0
            self.my_krw['avilable_krw'] = 0
            
        return r_balances
    
    def getNowPrice(self, ticker):
        # 현재가 조회
        try:
            price = python_bithumb.get_current_price([ticker])
            print(price)

            return price
        except:
            print("현재가 조회시 오류가 발생하였습니다.")

            return 0
        
    def getKRW(self, r):
        # 현재 원화 잔고를 얻어온다. 
        for i in range(len(r)):
            if r[i]['coin_type'] == 'KRW':
                money = r[i]['krw_balance']
                return money
    
    def getCoinProfit(self, r, coin):
        # 현재 코인의 수익률을 얻어온다.
        #print(coin)
        #print(len(r))
        for i in range(len(r)):
            #print(i)
            #print(r[i]['coin_type'])
            if r[i]['coin_type'] == coin:
                print(r[i]['coin_type'])
                profit = r[i]['profit']
                return profit
            #else:
        
        return -1000
            
            
    def getCoinVolume(self, r, coin):
        # 현재 보유한 코인의 수량을 얻어온다. 
        for i in range(len(r)):
            if r[i]['coin_type'] == coin:
                print(r[i]['coin_balance'])
                volume = r[i]['coin_balance']
                return volume
        
        return -1
    
    def getCoinAmount(self, r, coin):
        # 현재 보유한 코인의 보유 금액을 얻어온다.
        for i in range(len(r)):
            if r[i]['coin_type'] == coin:
                print(coin)
                print(r[i]['coin_amount'])
                amount = r[i]['coin_amount']
                return amount
        
        return -1
    
    def buyOrderMarket(self, t, volume):
        print("시장가주문")
        # t 는 코인명 예 "KRW-BTC"
        # volume 는 매수 금액. 원화로 환산하여 주문한다.
        try:
            r = bithumb.buy_market_order(t, volume)
            print(r)
            log.debug(r)
            log.debug("시장가 매수 주문. %s 의 %f 원 매수" % (t, volume))
            send_message("시장가 매수 주문. %s 의 %f 원 매수" % (t, volume))

            self.buy_flag = True
        except:
            print("매수 주문이 실패하였습니다.")
            self.buy_flag = False
            

            
    def sellOrderMarket(self, t, volume):
        print("시장가매도")
        # t는 코인의 종류(티커) 예를 들면 이더리움은 KRW-ETH, volume 은 보유 수량
        # volume에는 매도할 수량을 적는다. 최소 매도 수량은 원화로 5,000원 이상이어야 한다. 
        try:
            r = bithumb.sell_market_order(t, volume)
            print(r)
            log.debug(r)
            log.debug("시장가 매도 주문. %s 의 보유수량 %f 매도" % (t, volume))
            send_message("시장가 매도 주문. %s 의 보유수량 %f 매도" % (t, volume))

            #self.buy_flag = False
        except:
            print("매도 주문이 실패하였습니다.")
            self.buy_flag = True
            
            
    def trLoop(self):
        # 비트코인 실시간 정보를 등록합니다.
        wm = WebSocketManager("ticker", ["BTC_KRW"])
        
        while True:
            try:
                data = wm.get()

                print(f"[{data['content']['date']}]/[{data['content']['time']}] 코인:{data['content']['symbol']}, 전일종가:{data['content']['prevClosePrice']}, 시가:{data['content']['openPrice']}, 고가:{data['content']['highPrice']}, 저가:{data['content']['lowPrice']}, 종가(현재가):{data['content']['closePrice']}")

            except:
                err = traceback.format_exc()
                log.debug(str(err))
                send_message("크리티컬 오류 발생! 로그를 확인하기 바랍니다. 자동 종료 합니다.")

                wm.terminate()   # 멀티 프로세스 종료



def daemon():
    # daemon
    pid = os.fork()

    if pid > 0:
        exit(0)
    else:
        sys.stdin.flush()
        sys.stdout.flush()

        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        with open(pid_file, 'w') as write:
            write.write(str(os.getpid()))


def ps_checker(psname, cmdname):
    #process_name = 'python'  # 찾고 싶은 프로세스 이름

    count = 0
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == psname:
            cmdline = proc.cmdline()
            if cmdline[1] == cmdname:
                #print(psname)
                print(proc.cmdline())
                count += 1

    print(f"이름이 '{psname}'인 프로세스 개수: {count}")
    return count


def handle_sigchld(signum, frame):
    """SIGCHLD 시그널 핸들러 - 종료된 자식 프로세스 회수"""
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            log.debug(f"부모 프로세스 {os.getpid()}: 자식 프로세스 {pid} 종료 (상태: {status})")
            
            # 여기에 코드를 삽입하여 부모 프로세스를 Kill
        except ChildProcessError:
            break


def test():
    c = trCoinBit()
    r = c.getAccBalance()

    c.trLoop()

    

def run_daemon_loop():
    daemon()
    c = trCoinBit()
    c.trLoop()

def main():
    #run_daemon_loop()
    test()


if __name__ == "__main__":
    main()
