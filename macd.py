from tools import EMA,SMA

#MACD

#Ex: period2=26 and period1=12
class MACDindicator: 
  def __init__(self, periodSmall,periodBig,periodSignal,closes):
    self.EMA_p1 = periodSmall
    self.EMA_p2 = periodBig
    self.MACD_p = periodSignal
    self.EMA1 = SMA(closes,EMA_p1)
    self.EMA2 = SMA(closes,EMA_p2)
    self.MACD = self.EMA2 - self.EMA1
    self.signal = SMA(closes,MACD_p) #Fix this
    self.primed = False
    
  def addClose(close):
    self.EMA1 = EMA(close,self.EMA1,self.EMA_p1)
    self.EMA2 = EMA(close,self.EMA2,self.EMA_p2)
    self.MACD = self.EMA2 - self.EMA1
    self.signal = EMA(MACD,self.signal,self.MACD_p)
    
  def getOpinion():
    
    
    
        
    
    

