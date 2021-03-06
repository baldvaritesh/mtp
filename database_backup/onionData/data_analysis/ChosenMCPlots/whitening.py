'''
@	Note that this file is particularly for demo purposes
@	Not a general purpose file
@	Analysis based on Centre 50 and Corresponding Mandis 279, 376
'''

import chosenmcplots as cp
import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
import plotting as plt2
from datetime import datetime
from collections import Counter
import statsmodels as sm
import scipy, numpy as np
from scipy import signal
from sklearn.decomposition import FastICA, PCA


def RemoveNullsWithFirstValue(series):
	if(np.isfinite(series[7][0]) == True):
		return series
	for i in xrange(0 , len(series[7])):
		if(np.isfinite(series[7][i]) == False):
			continue
		else:
			value = series[7][i]
			for j in xrange(0,i):
				series[7][j] = value
			break
	return series

def ZeroMean(series, ind):
	mean = series[ind].mean()
	series[ind] -= mean
	return series

def PreProcess(series):
	eig_val_cov, eig_vec_cov = np.linalg.eig(series.cov())
	D = [[0.0 for i in xrange(0, len(eig_val_cov))] for j in xrange(0 , len(eig_val_cov))]
	for i in xrange(0, len(eig_val_cov)):
		D[i][i] = eig_val_cov[i]
	DInverse = np.linalg.matrix_power(D, -1)
	DReq = scipy.linalg.sqrtm(D)
	V = np.dot( np.dot(eig_vec_cov, DReq) , eig_vec_cov.T)
	series = series.apply(lambda row: np.dot(V, row.T).T, axis=1)
	return series


def ICA(seriesInp, n, days):
	if(len(seriesInp) != days):
		print 'Input is not correctly oriented'
		return

	ica = FastICA(n_components=n)
	S_ = ica.fit_transform(seriesInp)
	A_ = ica.mixing_
	series2 = np.dot(S_, A_.T)

	#	Get the residuals
	for i in xrange(0,len(seriesInp)):
		for j in xrange(0,len(seriesInp.T)):
			series2[i][j] -= seriesInp[i][j]

	return (series2, S_, A_)


'''Create a window around the series of factor'''
def CreateWindow(seriesInp, factor, days):
	if(len(seriesInp) != days):
		print 'Input is not correctly oriented'
		return

	window = np.zeros(shape=(len(seriesInp), len(seriesInp.T)))
	for i in xrange(0, len(seriesInp)):
		for j in xrange(0, len(seriesInp.T)):
			window[i][j] = abs(seriesInp[i][j] * factor)

	return window


''' Extract anomalies is not a general function '''
def ExtractAnomalies(residuals, window, index, days):
	anomalies = []
	idx = pd.date_range('2006-01-01', '2015-06-23')
	# idx2 = [0] * days
	for i in xrange(0, days):
		if(abs(residuals.T[index][i]) > window.T[index][i]):
			anomalies.append(idx[i])
			# idx2[i] = 1.0
	# lets plot the anomalies
	# plt.plot(idx2)
	# plt.show()
	return anomalies

def ExtractAnomalies3(residuals, window, index, days, val):
	anomalies = []
	idx = pd.date_range('2006-01-01', '2015-06-23')
	idx2 = [-2000] * days
	for i in xrange(0, days):
		if(abs(residuals.T[index][i]) > window.T[index][i]):
			anomalies.append(idx[i])
			idx2[i] = val 
	return idx2

def ExtractAnomalies2(residuals, index, days):
	anomalies = []
	idx = pd.date_range('2006-01-01', '2015-06-23')
	win = sum(abs(i) for i in resid.T[index]) / 3461
	for i in xrange(0, days):
		if(abs(residuals.T[index][i]) > window.T[index][i]):
			anomalies.append(idx[i])
	return anomalies

def RemoveNaNsFront(series, idx):
	index = 0
	while True:
		if(not np.isfinite(series[idx][index])):
			index += 1
		else:
			break
	for i in xrange(0, index):
		series[idx][i] = series[idx][index]
	return series


''' Get the centres and mandis '''
c = cp.cs
m = cp.ms

''' Interpolate all the present centres for now '''
for x in c:
	x[2] = x[2].replace('0.0', np.NaN, regex=True)
	x[2] = x[2].interpolate(method='pchip')
	x[2][0] = x[2][1]

for mandis in m:
	for x in mandis:
		x[2] = x[2].replace('0.0', np.NaN, regex=True)
		x[2] = x[2].interpolate(method='pchip')
		x[7] = x[7].replace('0.0', np.NaN, regex=True)
		x[7] = x[7].interpolate(method='pchip')
		x = RemoveNaNsFront(x, 2)
		x = RemoveNaNsFront(x, 7)



# Get the current values in a particular data frame
#	centres contains the original data frame // mean is centered
#	centres2 contains the whitened data frame

centres = c[0].copy()
centres[0] = centres[2]
for i in xrange(1, 5):
	centres[i] = c[i][2]
for i in xrange(0,5):
	centres = ZeroMean(centres, i)
centres2 = PreProcess(centres).as_matrix()

''' Initialise plotting library '''
# plt2.Init(len(centres2),2006)


''' Check if any NaNs exist '''
#
#	c.isnull().values.any()
#

