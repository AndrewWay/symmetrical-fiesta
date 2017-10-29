import os
import numpy as np
import pandas as pd
import pickle
import quandl
from datetime import datetime

import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt

py.init_notebook_mode(connected=True)

# Pickle used to serialize and save downloaded data as a file

def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

# Pull Kraken BTC price exchange data
btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')
# btc_usd_price_kraken.tail()

#Chart the BTC pricing data
btc_trace = go.Scatter(x=btc_usd_price_kraken.index, y=btc_usd_price_kraken['Weighted Price'])
# py.iplot([btc_trace])



# Pull pricing data for 3 more BTC exchanges
exchanges = ['COINBASE','BITSTAMP','ITBIT']

exchange_data = {}

exchange_data['KRAKEN'] = btc_usd_price_kraken

for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df




def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
        
    return pd.DataFrame(series_dict)

# Merge the BTC price dataseries' into a single dataframe
btc_usd_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')


# Remove "0" values
btc_usd_datasets.replace(0, np.nan, inplace=True)

# Calculate the average BTC price as a new column
btc_usd_datasets['avg_btc_price_usd'] = btc_usd_datasets.mean(axis=1)


# Plot the average BTC price
btc_trace = go.Scatter(x=btc_usd_datasets.index, y=btc_usd_datasets['avg_btc_price_usd'])

#time=btc_usd_datasets['Date']

short_period=10
long_period=26
signal_period=9

btc=btc_usd_datasets['avg_btc_price_usd']
clean_data=[]

time=btc.keys()
clean_time=[]

#Remove all nans from data
for i in range(0,len(btc)-1):
  if str(btc[i]) != 'nan':
    clean_data.append(btc[i])
    clean_time.append(time[i])    
   

def EMA(n,dat,t0):
    setsize = len(dat)
    ema=[]
    
    period=n
    sma=0
    sma_start=t0-period
    #calculate initial EMA (SMA)
    for i in range(sma_start,t0):
      sma=sma+dat[i]
    
    sma=sma/period
        
    if str(sma) == 'nan':
      ema=[0]
      return ema
       
    #Calculate the EMA
    multiplier=2/(period+1)
    ema.append(sma)
    ema_index=0
    
    for i in range(t0,setsize):
      if str(dat[i]) != 'nan':
        old_ema=ema[ema_index]
        current_close=dat[i]
        new_ema=(current_close-old_ema)*multiplier+old_ema
        ema.append(new_ema)
        ema_index=ema_index+1
    return ema
        
initial_time=long_period
macd=[]
zero_line=[]

if len(btc) >= long_period :
    ema_short=EMA(short_period,clean_data,initial_time)
    ema_long=EMA(long_period,clean_data,initial_time)
    for i in range(0,len(ema_short)-1):
        macd.append(ema_short[i]-ema_long[i])
        zero_line.append(0)

    signal=EMA(signal_period,macd,initial_time)

print(len(clean_data))
print(len(macd))
print(len(signal))
buy_period=10
time_counter=1
dca_amt=[0]
macd_amt=[0]

days=len(clean_data)

macd_trigger_threshold=0.05

starting_funds=10000
macd_funds=starting_funds
dca_funds=starting_funds
buy_amount=starting_funds/(days/buy_period)
dca_asset_value=[0]
macd_cross=0

macd_net_worth=[macd_funds]

#SIMULATION
for i in range(0,len(clean_data)-1):
    
  #Dollar cost averaging algorithm
  if time_counter == buy_period:
      coin_price=clean_data[i]
      coin_amount=buy_amount/coin_price
      dca_funds=dca_funds-buy_amount
      dca_amt.append(dca_amt[-1]+coin_amount)
      dca_asset_value.append(dca_amt[-1]*coin_price)
      time_counter=1
  
  time_counter=time_counter+1
  
  
  #MACD trading algorithm
  macd_diff=(macd[i]-signal[i])/macd[i]
  if abs(macd_diff) >=macd_trigger_threshold :
    coin_price=clean_data[i]
    if macd_diff < 0 :
      if macd_cross == 1 :
        #Negative cross. Sell
        if macd_amt[-1] >= buy_amount : #check if you have enough
          macd_funds=macd_funds+buy_amount
          sold_coin_amount=buy_amount/coin_price
          macd_amt.append(macd_amt[-1]-sold_coin_amount)
        else :
          sold_coin_amount=macd_amt[-1]
          sold_coin_value=sold_coin_amount*coin_price
          macd_funds=macd_funds+sold_coin_value
          macd_amt.append(macd_amt[-1]-sold_coin_amount)   
      
      macd_cross=-1
    if macd_diff > 0 :
      if macd_cross == -1 :
        #Positive cross. buy
        if macd_funds >= buy_amount : #check if you have enough
          macd_funds=macd_funds-buy_amount
          bought_coin_amount=buy_amount/coin_price
          macd_amt.append(macd_amt[-1]+bought_coin_amount)
        else :
          bought_coin_amount=macd_amt[-1]
          bought_coin_value=bought_coin_amount*coin_price
          macd_funds=macd_funds-bought_coin_value
          macd_amt.append(macd_amt[-1]+bought_coint_amount)        
      macd_cross=1
  macd_net_worth.append(macd_amt[-1]*coin_price+macd_funds)     
      
      
      
print(macd_funds)
print(dca_funds)
plt.plot(dca_asset_value)
plt.plot(macd_net_worth)
plt.ylabel('Value USD')
plt.xlabel('Index')
plt.show()
      
        




