from tools import EMA,SMA
from macd import MACDindicator
import time
import numpy as np
import csv

closes = []
dates = []
with open('macd.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        closes.append(row[1])
        dates.append(row[0])
closes = np.array(closes)
closes = closes.astype(np.float)

primerCloses = closes[slice(0,34)]
primerDates = dates[slice(0,34)]


macd = MACDindicator(12,26,9,primerCloses)

for i in range(34, len(closes)):
  currentClose = closes[i]
  print(dates[i], currentClose)
  macd.addClose(currentClose)

  #macd.updateOpinion()
  time.sleep(5)
  
