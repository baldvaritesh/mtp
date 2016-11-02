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


def PlotICs():
  # plt.subplot(211)
  # plt.plot(lag_acf)
  # plt.axhline(y=0,linestyle='--',color='gray')
  # plt.axhline(y=-1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')
  # plt.axhline(y=1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')
  # plt.title('IC1')
  return

def PlotResiduals():
  return

