from tools import EMA,SMA
import numpy as np
#MACD

#Ex: period2=26 and period1=12
class MACDindicator:

  crit_MACDrise = 0.5
  crit_priceDivergence = 0.25
  crit_cross = 3#Max number time units to qualify cross as "new"
  
  #Weights for decision making
  weight_cross = 3
  weight_divergence = 3
  weight_MACDrise = 3 
  
  def __init__(self, periodShort,periodLong,periodSignal,closes):
    self.EMA_shortp = periodShort
    self.EMA_longp = periodLong
    self.MACD_p = periodSignal
    self.prime(closes)
    
    self.crossAge = 0#How "old" the most recent cross is
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
    self.MACDold = self.MACD
    self.MACD = self.EMAshort - self.EMAlong
    self.signal = EMA(self.MACD,self.signal,self.MACD_p)
    
    self.updateAnalysisCriteria(close)
    self.updateOpinion()
    
  def updateAnalysisCriteria(self,close):
    #Price rise
    self.MACDchange = self.MACD - self.MACDold
    
    #Divergence
    self.divergence = (self.MACD - close)/self.MACD
    
    #Crossover
    if(self.MACD > self.signal):
      if(self.crossUnder == True):
        self.crossUnder = False
        self.crossAge = 0
      else:
        self.crossAge = self.crossAge + 1
    else:
      if(self.crossUnder == False):
        self.crossUnder = True
        self.crossAge = 0
      else:
        self.crossAge = self.crossAge + 1
        
  def updateOpinion(self):
      
    if(self.MACDchange >= self.crit_MACDrise):
      print("MACD dramatically rising; security is overbought")
      
    if(np.abs(self.divergence) >= self.crit_priceDivergence):
      print("Price is diverging")
      
    if(self.crossAge <= self.crit_cross):
      if(self.crossUnder == True):
        print("MACD has recently crossed below signal")
      else:
        print("MACD has recently crossed above signal") 
      
    else:
      print("No recent cross")
        
      
        
        
    
        
    
    

