import math
import time
import config

from fyers_api import fyersModel
from fyers_api import accessToken
from fyers_api.Websocket import ws
from tradeUtils import *


fyres
this_stock_name
direction
avg_ltp
live_data
trade_count
fyresSocket
is_trade_taken
order_response
is_trade_complete = False
symbol = []
threshold_level = 0


def place_order_at_market_value():
    global fyres
    global this_stock_name
    global direction
    global avg_ltp

    return fyres.place_order(get_order_data_json(this_stock_name,
                                                 80000,
                                                 avg_ltp,
                                                 direction))


def gorilla_strategy():
    global fyres
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
        order_response = place_order_at_market_value()
        order_id = order_response.get("id")
        order_data = {}
        order_data["id"] = order_id
        is_order_placed = False

        while not is_order_placed:
            time.sleep(2)
            order_book = fyres.order_book(data=order_data).get("orderBook")[0]
            order_positions = fyres.positions()
            if order_book.get('message') == 'TRADE CONFIRMED' and len(order_positions.get("netPositions")) > 0:
                is_order_placed = True
                is_trade_taken = True
                threshold_level = math.floor(order_positions.get("netPositions").get("avgPrice"))

        trade_count = trade_count + 1

    else:
        if direction == 3:
            if ltp >= threshold_level + (0.025 * threshold_level):
                exit_data = {}
                fyers.exit_positions(exit_data)
                print("Congrats we hit the Target for the day !")
                fyersSocket.unsubscribe(symbol=symbol)
                is_trade_complete = True
            elif ltp <= threshold_level - (0.0019 * threshold_level):
                exit_data = {}
                fyers.exit_positions(exit_data)
                print("Oops, We hit the stoploss for trade : " + trade_count + "!")
                direction = 6
                is_trade_taken = False
                if trade_count >= 3:
                    fyersSocket.unsubscribe(symbol=symbol)
                    is_trade_complete = True


        elif direction == 6:
            if ltp <= threshold_level - (0.025 * threshold_level):
                exit_data = {}
                fyers.exit_positions(exit_data)
                print("Congrats we hit the Target for the day :)")
                fyersSocket.unsubscribe(symbol=symbol)
                is_trade_complete = True
            elif ltp >= threshold_level + (0.0019 * threshold_level):
                exit_data = {}
                fyers.exit_positions(exit_data)
                print("Oops, We hit the stoploss for trade : " + trade_count + "!")
                direction = 3
                is_trade_taken = False
                if trade_count >= 3:
                    fyersSocket.unsubscribe(symbol=symbol)
                    is_trade_complete = True



def data_feed(msg):
    for symbol_data in msg:
        live_data[symbol_data['symbol']] = {"LTP": symbol_data['ltp']}


if __name__ == '__main__':
    session = accessToken.SessionModel(client_id=config.client_id,
                                       secret_key=config.secret_key,
                                       redirect_uri=config.redirect_uri,
                                       response_type='code',
                                       grant_type='authorization_code')
    response = session.generate_authcode()
    print(response)
    auth_code = input("Enter Auth Code : ")
    session.set_token(auth_code)
    response = session.generate_token()

    access_token = response["access_token"]
    print("Access Token : " + access_token)

    fyers = fyersModel.FyersModel(client_id=config.client_id, token=access_token)
    print(fyers.get_profile())

    print(fyers.funds())

    ws_access_token = f"{config.app_id}:{access_token}"
    print(ws_access_token)
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
    input("Press enter start the trade : ")

    current_direction = 0
    while current_direction != 3 or current_direction != 9:
        current_direction = int(input("3 for Long, 9 for Short : "))
    direction = current_direction

    while not is_trade_complete:
        print("Executing the strategy......")
        gorilla_strategy()

