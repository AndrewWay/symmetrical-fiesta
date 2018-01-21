from tools import EMA,SMA

#MACD

#Ex: period2=26 and period1=12
class MACDindicator:
 
  def __init__(self, periodShort,periodLong,periodSignal,closes):
    self.EMA_shortp = periodShort
    self.EMA_longp = periodLong
    self.MACD_p = periodSignal
    self.prime(closes)
    
    self.crossUnder = False #Used to keep track of whether MACD line has crossed under signal line
    self.divergence = 0 # Fraction of (MACD - close) / MACD
    self.opinion = "HOLD"
    self.acceleration = 0
    
  #Primer for EMA, MACD, signal
  #Basically just seeds long EMA, short EMA, signal, MACD
  def prime(self,closes):
    sliceObj = slice(0, len(closes)-self.MACD_p+1) 
    EMAprimerData = closes[sliceObj]

    self.EMAshort = SMA(EMAprimerData,self.EMA_shortp)
    self.EMAlong = SMA(EMAprimerData,self.EMA_longp)
    self.MACDHolder = []
    self.MACD = self.EMAshort - self.EMAlong
    self.MACDHolder.append(self.MACD)
    
    for i in range(len(closes)-self.MACD_p+1,len(closes)):
      self.EMAshort = EMA(closes[i],self.EMAshort,self.EMA_shortp)
      self.EMAlong = EMA(closes[i],self.EMAlong,self.EMA_longp)
      self.MACD = self.EMAshort - self.EMAlong
      self.MACDHolder.append(self.MACD)
    
    self.signal = SMA(self.MACDHolder,self.MACD_p)

  def addClose(self,close):
    self.EMAshort = EMA(close,self.EMAshort,self.EMA_shortp)
    self.EMAlong = EMA(close,self.EMAlong,self.EMA_longp)
    self.MACD = self.EMAshort - self.EMAlong
    self.signal = EMA(self.MACD,self.signal,self.MACD_p)
    
    #self.updateAnalysisCriteria(close)
    #self.updateOpinion()
    
  def updateAnalysisCriteria(self,close):
    self.divergence = (self.MACD - close)/self.MACD
    if(self.MACD > self.signal):
      self.crossunder = False
    else:
      self.crossunder = True
    
    
  #def updateOpinion():
    
    
        
    
    

