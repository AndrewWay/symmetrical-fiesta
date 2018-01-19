#TOOLS

#Return the SMA average using the elements 
#from the end of the array.
#Period is the number of elements to use in the SMA
def SMA(prices,period):
  end = len(prices)
  start = end - period
  
  total = 0
  if(start >= 0):
    for i in range(start,end):
      total = total + prices[i]
  else:
    print('ERROR: Number of elements less than period')
  
  return total/period
    
#Exponential Moving Average Function
#Given a previous EMA, the current close, and a period,
#return the current EMA
def EMA(close, oldEMA, period):
    multiplier=2/(period+1)
    newEMA=(close-oldEMA)*multiplier+oldEMA
    
    return newEMA

p = [1,2,3,4,5,6,7,8,9,10]
sma = SMA(p,9)
ema = EMA(9.5,sma,9)
print(sma)
print(ema)
  
