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
    print('SMA error: Number of elements less than period',period)
    print('Creating SMA using given ',end,' elements')
    for i in range(0,end):
      total = total + prices[i]
  return total/period
    
#Exponential Moving Average Function
#Given a previous EMA, the current close, and a period,
#return the current EMA
def EMA(close, oldEMA, period):
    multiplier=2/(period+1)
    newEMA=(close-oldEMA)*multiplier+oldEMA
    
    return newEMA
  
