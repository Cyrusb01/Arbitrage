# from gspread.models import Worksheet
import websocket, json 
# import gspread 
# from oauth2client.service_account import ServiceAccountCredentials 
import asyncio
import websockets 
import aiohttp
import time


#----------------------------------------------------------------Gspread-------------------------------------------------------------------------------------

# scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
# client = gspread.authorize(creds)

# spreadsheet = client.open("arb matrix").sheet1


#----------------------------------------------------------------Asynchronous ---------------------------------------------------------------------------------
#get bids and asks and compare those

def minute_passed(oldepoch):
    return time.time() - oldepoch >= 20

connections = set()
connections.add('wss://stream.binance.com:9443/ws/btcusdt@bookTicker')
connections.add('wss://ws-feed.pro.coinbase.com')
connections.add('wss://ws.kraken.com/')
connections.add('wss://api.gemini.com/v1/marketdata/BTCUSD?top_of_book=true&bids=true&offers=true')
connections.add('wss://ftx.com/ws/')




async def handle_socket(uri, ):
    print("Started Socket:", uri)

    global latest_binance_price 
    latest_binance_price = 0
    global latest_coinbase_price 
    latest_coinbase_price = 0
    global latest_krakken_price 
    latest_krakken_price = 0
    global latest_gemini_price 
    latest_gemini_price = 0
    global latest_ftx_price 
    latest_ftx_price = 0

    global coinbase_bid
    
    global coinbase_ask
    global binance_bid
    global binance_ask
    global kraken_bid
    global kraken_ask
    global ftx_ask
    global ftx_bid
    global gemini_ask
    global gemini_bid
    
    async with websockets.connect(uri) as websocket:
        # print("-----------------------------------------------------------------")
        if (uri == 'wss://ws-feed.pro.coinbase.com'): #Subscribe to Coinbase
            subscribe_message = {
                'type' : 'subscribe',
                'channels' : [{'name' : 'ticker',
                        'product_ids' : ['BTC-USD'] }]
            }
            await websocket.send(json.dumps(subscribe_message))
        
        if (uri == 'wss://ws.kraken.com/'): #Subscribe to Krakken
            await websocket.send('{"event":"subscribe", "subscription":{"name":"spread"}, "pair":["BTC/USD"]}')
        
        if (uri == 'wss://ftx.com/ws/'): #Subscribe to FTX
            await websocket.send('{"op": "subscribe", "channel": "ticker", "market": "BTC/USD"}')
        
        seconds = time.time()
        
        async for message in websocket:
            if (uri == 'wss://ws-feed.pro.coinbase.com'):
                message_dict_2 = json.loads(message)
                #print(message)
                values = list(message_dict_2.values())
                counter = 0
                if (not (values[0] == 'subscriptions')): #first message is an intro subscription
                    for i in range(len(values)):
                         
                        if (counter == 3):
                            latest_coinbase_price = values[i]
                        if (counter == 9):
                            #print("best bid", values[i])
                            coinbase_bid = values[i]
                        if (counter == 10):
                            #print("best bid", values[i])
                            coinbase_ask = values[i]
                        counter += 1
                
            if (uri == 'wss://stream.binance.com:9443/ws/btcusdt@bookTicker'):
                message_dict = json.loads(message)
                binance_bid = message_dict['b']
                binance_ask = message_dict['a']
                latest_binance_price = binance_bid
                #print("binance")

            if (uri == 'wss://ws.kraken.com/'):
                message_dict = json.loads(message)
                if (not isinstance(message_dict, dict)): #sends the heartbeats 
                    kraken_bid = message_dict[1][0]
                    kraken_ask = message_dict[1][1]
                    # price = message_dict_2[1][0][0]
                    latest_krakken_price = kraken_bid
                #print("Krakken")          

            if (uri == 'wss://api.gemini.com/v1/marketdata/BTCUSD?top_of_book=true&bids=true&offers=true'):
                message_dict = json.loads(message)
                if(message_dict["events"][0]["side"] == "ask"):
                    gemini_ask = message_dict["events"][0]["price"]
                if(message_dict["events"][0]["side"] == "bid"):
                    gemini_bid = message_dict["events"][0]["price"]
                
                latest_gemini_price = message_dict["events"][0]["price"]
                #print(latest_gemini_price)

            if (uri == 'wss://ftx.com/ws/'):
                message_dict = json.loads(message)
                #print(message)
                if(len(message_dict) != 3): #this lets us ignore the first 
                    
                    ftx_bid = message_dict["data"]["bid"]
                    ftx_ask = message_dict["data"]["ask"]

                    latest_ftx_price = ftx_ask
    
            if True:
                seconds = time.time()
                if latest_binance_price != 0 and latest_coinbase_price != 0 and latest_krakken_price != 0 and latest_gemini_price != 0 and latest_ftx_price != 0:

                    
                    prices = {"Binance" : float(latest_binance_price), "Coinbase" : float(latest_coinbase_price), "Krakken" : float(latest_krakken_price), "Gemini" : float(latest_gemini_price),  "FTX" : float(latest_ftx_price)}
                    # print(list(prices.items()))
                    largest_diff = 0
                    diff_exchanges = ""
                    for key in prices.keys():
                        # print(key, ":", prices[key])
                        for key_ in prices.keys():
                            # print(key, ":", prices[key])
                            if ((prices[key] - prices[key_]) / prices[key_]) * 100 > largest_diff:
                                largest_diff = ((prices[key] - prices[key_]) / prices[key_]) * 100
                                diff_exchanges = key + "/" + key_




                    print("Binance Latest Price: ", latest_binance_price)
                    print("Coinbase Latest Price: ", latest_coinbase_price)
                    print("Krakken Latest Price: ", latest_krakken_price)
                    print("Gemini Latest Price: ", latest_gemini_price)
                    print("FTX Latest Price: ", latest_ftx_price)
                    print("GREATEST OPPORTUNITY ", diff_exchanges, " : ", largest_diff, "%")

                    print("--------------------------------------------------")
                    # return render_template("index.html", coin = latest_coinbase_price, bin = latest_binance_price, krak = latest_krakken_price, gem = latest_gemini_price, ftx = latest_ftx_price)

        
                    # spreadsheet.update_cell(2, 13, binance_bid)
                    # spreadsheet.update_cell(3, 13, latest_binance_price)
                  
                    # spreadsheet.update_cell(2, 11, coinbase_bid)
                    # spreadsheet.update_cell(3, 11, coinbase_ask)
                
                    # spreadsheet.update_cell(2, 12, kraken_bid)
                    # spreadsheet.update_cell(3, 12, kraken_ask)
                
                    # spreadsheet.update_cell(2, 14, gemini_bid)
                    # spreadsheet.update_cell(3, 14, gemini_ask)
    
                    # spreadsheet.update_cell(2, 15, ftx_bid)
                    # spreadsheet.update_cell(3, 15, ftx_ask)

                # if(latest_binance_price != 0):
                #     spreadsheet.update_cell(5, 2, latest_binance_price)
                #     spreadsheet.update_cell(2, 5, latest_binance_price)
                # if(latest_coinbase_price != 0):
                #     spreadsheet.update_cell(3, 2, latest_coinbase_price)
                #     spreadsheet.update_cell(2, 3, latest_coinbase_price)
                # if(latest_krakken_price != 0):
                #     spreadsheet.update_cell(4, 2, latest_krakken_price)
                #     spreadsheet.update_cell(2, 4, latest_krakken_price)
                # if(latest_gemini_price != 0):
                #     spreadsheet.update_cell(6, 2, latest_gemini_price)
                #     spreadsheet.update_cell(2, 6, latest_gemini_price)
                # if(latest_ftx_price != 0):
                #     spreadsheet.update_cell(7, 2, latest_ftx_price)
                #     spreadsheet.update_cell(2, 7, latest_ftx_price)


                #print("Binance Latest Price: ", latest_binance_price)
                
            
async def handler():
    await asyncio.wait([handle_socket(uri) for uri in connections])

asyncio.get_event_loop().run_until_complete(handler())
