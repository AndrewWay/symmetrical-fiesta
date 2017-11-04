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

btc=btc_usd_datasets['avg_btc_price_usd']
clean_data={}

time=btc.keys()
clean_time=[]

print('cleaning data...')
#Remove all nans from data
for i in range(0,len(btc)-1):
  if str(btc[i]) != 'nan':
    t=time[i]
    clean_data[t]=btc[i]
    clean_time.append(t)    
print('data cleaned.')
print('data length: ',len(clean_data))
print('time array length: ',len(clean_time))

#Exponential Moving Average Function
#Takes a data set, and returns a key-value array
#args: n, period of EMA
#time, array containing dates
#dat, array containing price data
#period, period of exponential moving average
#t0, the index of the time from which to start calculating EMA data
def EMA(period,time,dat,t0):
    setsize = len(dat)
    ema={}

    sma=0
    sma_start=t0-period
    #calculate initial EMA (SMA)
    for i in range(sma_start,t0):
      t=time[i]
      if t in dat:
        sma=sma+dat[t]
    
    sma=sma/period
        
    if str(sma) == 'nan':
      ema=[0]
      print('EMA at',t0,'is not a number')
      return ema
       
    #Calculate the EMA
    multiplier=2/(period+1)
    ema[time[t0]]=sma
    ema_index=t0
    
    for i in range(t0,setsize):
      t=time[i]
      if str(dat[t]) != 'nan':
        old_ema=ema[time[ema_index]]
        current_close=dat[t]
        new_ema=(current_close-old_ema)*multiplier+old_ema
        ema_index=i
        ema[time[ema_index]]=new_ema
    return ema

short_period=10
long_period=26
signal_period=9
initial_time=long_period
macd={}
zero_line={}

#Ensure number of data points >= to long period
if len(clean_data) >= long_period :
    #Create the short period EMA line
    print('creating',short_period,'day period EMA line')
    ema_short=EMA(short_period,clean_time,clean_data,initial_time)
    #Create the long period EMA line
    print('creating',long_period,'day period EMA line')
    ema_long=EMA(long_period,clean_time,clean_data,initial_time)
    #Create the MACD line
    print('creating MACD line')
    for i in range(0,len(clean_time)):
        t=clean_time[i]
        if t in ema_short and t in ema_long:
          ema_s=ema_short[t]
          ema_l=ema_long[t]
          macd[t]=ema_s-ema_l
          zero_line[t]=0
          
    if len(ema_short) != len(ema_long):
      print('WARNING: EMA_short length not equal to EMA_long')
    if len(ema_short) != len(macd):
      print('WARNING: EMA_short length not equal to MACD')  
    if len(ema_long) != len(macd):
      print('WARNING: EMA_long length not equal to MACD')  
    
    
    #Create the signal line
    print('creating',signal_period,'day signal line')
    signal=EMA(signal_period,clean_time,macd,initial_time)


#TRADING SIMULATOR 
print('beginning trading simulator')
buy_period=10 #parameter for DCA algorithm; make a buy every 10 time units
time_counter=1
dca_amt=[0]
macd_amt=[0]

days=len(clean_data)

macd_trigger_threshold=0.05 #Determines threshold to buy or sell

starting_funds=10000
macd_funds=starting_funds
dca_funds=starting_funds
buy_amount=starting_funds/(days/buy_period)
dca_asset_value=[0]
macd_cross=0

macd_net_worth=[macd_funds]
macd_diff=0
macd_counter=0

macd_buy_factor=0.02


#SIMULATION
for i in range(0,len(clean_data)-1):
  t=clean_time[i]
  #Dollar cost averaging algorithm
  if time_counter == buy_period:
    coin_price=clean_data[t]
    coin_amount=buy_amount/coin_price
    dca_funds=dca_funds-buy_amount
    dca_amt.append(dca_amt[-1]+coin_amount)
    dca_asset_value.append(dca_amt[-1]*coin_price)
    time_counter=0
  
  time_counter=time_counter+1
  
  
  #MACD trading algorithm

  
  if t in macd and t in signal:
    macd_diff=(macd[t]-signal[t])/abs(macd[t])
  
  if i == 533:
    print('i IS NOW 533')
    print(macd_diff)
  if abs(macd_diff) >= macd_trigger_threshold:
    coin_price=clean_data[t]
    if macd_diff < 0 : #if MACD minus Signal < 0
      if macd_cross == 1 : #and if MACD was previously positive
        #The the MACD has made a negative cross. Sell.
        macd_sell_amount=macd_amt[-1]*macd_buy_factor
        print('SELL ',macd_sell_amount,'@',coin_price,'T:',i)
        if macd_amt[-1] >= macd_sell_amount : #check if you have enough
          sold_coin_value=macd_sell_amount*coin_price #Calculate coin quantity to sell
          macd_amt.append(macd_amt[-1]-macd_sell_amount) #Remove the coin quantity from holdings
          macd_funds=macd_funds+macd_sell_amount #Increase fiat by buy amount
        else :
          sold_coin_amount=macd_amt[-1]
          sold_coin_value=sold_coin_amount*coin_price
          macd_funds=macd_funds+sold_coin_value
          macd_amt.append(macd_amt[-1]-sold_coin_amount)   
      
      macd_cross=-1#Store the fact that MACD minus signal < 0
    if macd_diff > 0 :
      if macd_cross == -1 :
        #Positive cross. buy
        macd_buy_price=macd_funds*macd_buy_factor
        if macd_funds >= macd_buy_price : #check if you have enough
          macd_funds=macd_funds-macd_buy_price
          bought_coin_amount=macd_buy_price/coin_price
          print('BUY',bought_coin_amount,'@',coin_price,'T:',i)
          macd_amt.append(macd_amt[-1]+bought_coin_amount)
        else :
          bought_coin_amount=macd_amt[-1]
          bought_coin_value=bought_coin_amount*coin_price
          macd_funds=macd_funds-bought_coin_value
          macd_amt.append(macd_amt[-1]+bought_coin_amount)        
      macd_cross=1
    macd_net_worth.append(macd_amt[-1]*coin_price+macd_funds)  
       
      
print('Final MACD funds:',macd_funds)
print('Final DCA funds:',dca_funds)
print('Final MACD coin quantity:',macd_amt[-1])
print('Final DCA coin quantity:',dca_amt[-1])
print('Final MACD networth: ',macd_funds+macd_amt[-1]*coin_price)
print('Final DCA networth: ',dca_funds+dca_amt[-1]*coin_price)

#TEMPORARY STUFF FOR PLOTTING/TESTING
#find better way

ema_short_tmp=[]
ema_long_tmp=[]
macd_tmp=[]
signal_tmp=[]
price_tmp=[]
zeros=[]
indices=[]
for i in range(0,len(clean_time)):
  t=clean_time[i]
  if t in macd: 
    if t in signal:
      if t in ema_short:
        if t in ema_long:
          if t in clean_data:
            ema_s=ema_short[t]
            ema_l=ema_long[t]
            mac=macd[t]
            sig=signal[t]
            p=clean_data[t]
            
            ema_short_tmp.append(ema_s)
            ema_long_tmp.append(ema_l)
            macd_tmp.append(mac)
            signal_tmp.append(sig)
            price_tmp.append(p)
            zeros.append(0)
            indices.append(i)
            
# END OF TEMPORARY STUFF

#plt.plot(ema_short_tmp,label='ema_short')
#plt.plot(ema_long_tmp,label='ema_long')
plt.plot(indices,macd_tmp,label='MACD')
plt.plot(indices,signal_tmp,label='Signal')
plt.plot(indices,price_tmp,label='Price')
plt.plot(indices,zeros)
plt.legend(loc='upper left')
plt.ylabel('Value USD')
plt.xlabel('Index')
#plt.show()
      
        




