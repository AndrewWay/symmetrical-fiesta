from tools import EMA,SMA
from macd import MACDindicator
closes = []

for i in range(0,30):
  closes.append(i)
 
print(closes) 

macd1 = MACDindicator(12,26,9,closes)


print(macd1.getEMA1(),macd1.getEMA2(),macd1.getMACD(),macd1.getSignal())

macd1.addClose(1)


print(macd1.getEMA1(),macd1.getEMA2(),macd1.getMACD(),macd1.getSignal())



