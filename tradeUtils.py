import datetime
import math


def get_stock():
    symbol = []
    stock_name = input("Enter Stock Name : ").upper()
    symbol.append("NSE:" + stock_name + "-EQ")
    print("Trading in Stock : " + symbol[0])
    return symbol


def get_avg_ltp(stock_name):
    avg_ltp = input(int("Average LTP for " + stock_name + " : "))
    return avg_ltp


def get_order_data_json(stock_name, capital, ltp, direction):
    quantity = (math.floor(capital / ltp)) * 4

    if direction == 3:
        side = 1
    else:
        side = -1

    data = {
        "symbol": stock_name,
        "qty": quantity,
        "type": 2,  # represents Market Order
        "side": side,  # 1 => Buy / -1 => Sell
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": "False",
        "stopLoss": 0,
        "takeProfit": 0
    }
    return data


'''
Method checks if time is not past 11Am. 
'''
def is_trade_within_time():
    now = datetime.datetime.now()
    today11am = now.replace(hour=14, minute=00, second=0, microsecond=0)
    if now < today11am:
        return True

    return False
