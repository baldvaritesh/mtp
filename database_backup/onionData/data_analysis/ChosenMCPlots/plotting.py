import chosenmcplots as cp
import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import statsmodels as sm
import scipy, numpy as np
from scipy import signal

labels = []
intervals = []

def Init(numDays, start):
  global labels, intervals
  # Adding two cause of the range of python
yrs = (numDays / 365) + 2
labels = [str(start + i) for i in xrange(0, yrs)]
intervals = [i*365 for i in xrange(0 , yrs)]
  return


def PlotICs(ics):
  plt.subplot(211)
  plt.plot(ics.T[0], label='IC1')
  plt.title('Delhi')
  plt.legend(loc='best')
  plt.xticks(intervals, labels)
  plt.ylabel('Price/Qtl')
  plt.xlabel('Years')
  plt.subplot(212)
  plt.plot(ics.T[1], label='IC2')
  plt.legend(loc='best')
  plt.xticks(intervals, labels)
  plt.ylabel('Price/Qtl')
  plt.xlabel('Years')
  plt.tight_layout()
  plt.show()
  return

plt.plot(priceanom1, label='Delhi Anomalies Prices', color='blue')
plt.plot(priceanom3, label='Mumbai Anomalies Prices', color='salmon')
plt.legend(loc='best')
plt.xticks(intervals, labels)
plt.xlabel('Years')
plt.ylabel('Anomaly Prices/Qtl')

def PlotResidual(seriesInp, window, index):
  #Create the negative window series
  reflector = lambda t: -1.0*t
  funReflector = np.vectorize(reflector)
  window2 = funReflector(window)

  plt.plot(seriesInp.T[index], label=('Centre' + str(index + 1)))
  plt.plot(window.T[index], linestyle='--', color='gray')
  plt.axhline(y=0,linestyle='--',color='gray')
  plt.plot(window2.T[index], linestyle='--', color='gray')
  plt.legend(loc='best')
  plt.xticks(intervals, labels)
  plt.show()
  return
