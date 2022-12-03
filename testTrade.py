import math
import time
import config

from fyers_api import fyersModel
from fyers_api import accessToken
from fyers_api.Websocket import ws
from tradeUtils import *
from loginToFyres import auto_login
from colorama import Fore, Back, Style


'''
Just a test replica of actual strategy for paper testing the actual strategy without actual capital being Involved.
'''

fyers = None
this_stock_name = None
direction = None
avg_ltp = None
live_data = None
trade_count = None
fyresSocket = None
is_trade_taken = None
order_response = None
is_trade_complete = False
symbol = []
threshold_level = 0


def place_order_at_market_value():
    print("PLacing order @ "+avg_ltp)
    '''global fyers
    global this_stock_name
    global direction
    global avg_ltp

    return fyers.place_order(get_order_data_json(this_stock_name,
                                                 config.capital,
                                                 avg_ltp,
                                                 direction))'''


def gorilla_strategy():
    global fyers
    global this_stock_name
    global direction
    global avg_ltp
    global live_data
    global trade_count
    global fyresSocket
    global is_trade_taken
    global threshold_level
    global order_response
    global symbol
    global is_trade_complete
    ltp = live_data.get(this_stock_name).get("LTP")

    if not is_trade_taken:
        place_order_at_market_value()
        #order_id = order_response.get("id")
        #order_data = {}
        #order_data["id"] = order_id
        is_order_placed = False

        while not is_order_placed:
            time.sleep(2)
            #order_book = fyers.order_book(data=order_data).get("orderBook")[0]
            #order_positions = fyers.positions()
            #if order_book.get('message') == 'TRADE CONFIRMED' and len(order_positions.get("netPositions")) > 0:
            if True:
                is_order_placed = True
                is_trade_taken = True
                #threshold_level = math.floor(order_positions.get("netPositions").get("avgPrice"))
                threshold_level = avg_ltp

        trade_count = trade_count + 1
        print(trade_count)

    else:
        if direction == 3:
            if ltp >= threshold_level + (0.025 * threshold_level):
                exit_data = {}
                #fyers.exit_positions(exit_data)
                print(Back.GREEN + "Exiting Positions @ "+ltp)
                print("Congrats we hit the Target for the day !")
                fyersSocket.unsubscribe(symbol=symbol)
                is_trade_complete = True
            elif ltp <= threshold_level - (0.0019 * threshold_level):
                exit_data = {}
                # fyers.exit_positions(exit_data)
                print(Fore.RED+"Exiting Positions @ " + ltp)
                print("Oops, We hit the stoploss for trade : " + trade_count + "!")
                direction = 6
                is_trade_taken = False
                if trade_count >= 3:
                    fyersSocket.unsubscribe(symbol=symbol)
                    is_trade_complete = True

        elif direction == 6:
            if ltp <= threshold_level - (0.025 * threshold_level):
                exit_data = {}
                # fyers.exit_positions(exit_data)
                print(Back.GREEN + "Exiting Positions @ " + ltp)
                print("Congrats we hit the Target for the day :)")
                fyersSocket.unsubscribe(symbol=symbol)
                is_trade_complete = True
            elif ltp >= threshold_level + (0.0019 * threshold_level):
                exit_data = {}
                # fyers.exit_positions(exit_data)
                print(Fore.RED + "Exiting Positions @ " + ltp)
                print("Oops, We hit the stoploss for trade : " + trade_count + "!")
                direction = 3
                is_trade_taken = False
                if trade_count >= 3:
                    fyersSocket.unsubscribe(symbol=symbol)
                    is_trade_complete = True


def data_feed(msg):
    print('Data : ')
    print(msg)
    for symbol_data in msg:
        live_data[symbol_data['symbol']] = {"LTP": symbol_data['ltp']}


if __name__ == '__main__':
    access_token = auto_login()
    print("Access Token : " + access_token)

    fyers = fyersModel.FyersModel(client_id=config.client_id, token=access_token)
    print(fyers.get_profile())

    print(fyers.funds())

    ws_access_token = f"{config.client_id}:{access_token}"
    data_type = "symbolData"
    run_background = False
    symbol = get_stock()
    this_stock_name = symbol[0]
    # avg_ltp = get_avg_ltp(this_stock_name)
    print("Trading on : " + this_stock_name)

    live_data = {}
    fyersSocket = ws.FyersSocket(access_token=ws_access_token, run_background=False, log_path="")
    fyersSocket.websocket_data = data_feed
    fyersSocket.subscribe(symbol=symbol, data_type=data_type)
    fyersSocket.keep_running()

    avg_ltp = live_data.get(this_stock_name).get("LTP")
    trade_count = 0
    is_trade_taken = False

    current_direction = 0
    while current_direction != 3 or current_direction != 6:
        current_direction = int(input("3 for Long, 6 for Short : "))
    direction = current_direction
    input("Press enter start the trade : ")

    while not is_trade_complete and is_trade_within_time():
        print("Executing the strategy......")
        gorilla_strategy()

    if not is_trade_within_time():
        exit_data = {}
        fyers.exit_positions(exit_data)
