from tools import EMA,SMA

#MACD

#Ex: period2=26 and period1=12
class MACDindicator:
 
  def __init__(self, periodSmall,periodBig,periodSignal,closes):
    self.EMA_p1 = periodSmall
    self.EMA_p2 = periodBig
    self.MACD_p = periodSignal
    self.prime(closes)
    
    self.crossUnder = False #Used to keep track of whether MACD line has crossed under signal line
    self.divergence = 0 # Fraction of (MACD - close) / MACD
    self.opinion = "HOLD"
    self.acceleration = 0
    
  #Primer for EMA, MACD, signal
  #Basically just seeds long EMA, short EMA, signal, MACD
  def prime(self,closes):
    sliceObj = slice(0, len(closes)-self.MACD_p) 
    primerData = closes[sliceObj]
    self.EMA1 = SMA(primerData,self.EMA_p1)
    self.EMA2 = SMA(primerData,self.EMA_p2)
    tmpHolder = []
    
    for i in range(len(closes)-self.MACD_p,len(closes)):
      self.MACD = self.EMA1 - self.EMA2
      tmpHolder.append(self.MACD)
      self.EMA1 = EMA(closes[i],self.EMA1,self.EMA_p1)
      self.EMA2 = EMA(closes[i],self.EMA2,self.EMA_p2)
    
    self.signal = SMA(tmpHolder,self.MACD_p)
  
  def addClose(self,close):
    self.EMA1 = EMA(close,self.EMA1,self.EMA_p1)
    self.EMA2 = EMA(close,self.EMA2,self.EMA_p2)
    self.MACD = self.EMA2 - self.EMA1
    self.signal = EMA(self.MACD,self.signal,self.MACD_p)
    
    self.updateAnalysisCriteria(close)
    self.updateOpinion()
    
  def updateAnalysisCriteria(self,close):
    self.divergence = (self.MACD - close)/self.MACD
    if(self.MACD > self.signal):
      self.crossunder = False
    else:
      self.crossunder = True
    
    
  def updateOpinion():
    
    
  def getEMA1(self):
    return self.EMA1
    
  def getEMA2(self):
    return self.EMA2
    
  def getMACD(self):
    return self.MACD
    
  def getSignal(self):
    return self.signal
  
    
    
        
    
    

