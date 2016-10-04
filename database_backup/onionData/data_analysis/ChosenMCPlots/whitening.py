'''
@	Note that this file is particularly for demo purposes
@	Not a general purpose file
@	Analysis based on Centre 50 and Corresponding Mandis 279, 376
'''

import chosenmcplots as cp
import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import statsmodels as sm
import scipy, numpy as np
from scipy import signal
from sklearn.decomposition import FastICA, PCA

''' get the dummy centre: 50 and two mandis: 279 (0) , 376 (2) '''
c = cp.cs
m = cp.ms

''' Interpolate all the present series '''
for x in c:
	x = x.replace('0.0', np.NaN, regex=True)
	x = x.interpolate(method='pchip')
	x[2][0] = x[2][1]

for mandis in m:
	for x in mandis:
		x[2] = x[2].replace('0.0', np.NaN, regex=True)
		x[2] = x[2].interpolate(method='pchip')
		x[7] = x[7].replace('0.0', np.NaN, regex=True)
		x[7] = x[7].interpolate(method='pchip')

''' Check if any NaNs exist '''
#
#	c.isnull().values.any()
#


def ZeroMean(series, ind):
	mean = series[ind].mean()
	series[ind] -= mean
	return series

def PreProcess(seriesC, seriesM):
	for i in xrange(0 , len(seriesM)):
		seriesC[i + 3] = seriesM[i][7]

	for i in xrange(2, len(seriesM) + 3):
		seriesC[i] = ZeroMean(seriesC, i)
	#
	#	Get the covariance matrices and eigen value decomposition
	#
	eig_val_cov, eig_vec_cov = np.linalg.eig(seriesC.cov())
	D = [[eig_val_cov[0],0.0,0.0], [0.0,eig_val_cov[1],0.0], [0.0,0.0,eig_val_cov[2]]]
	DInverse = np.linalg.matrix_power(D, -1)
	DReq = scipy.linalg.sqrtm(D)
	V = np.dot( np.dot(eig_vec_cov, DReq) , eig_vec_cov.T)

	#
	#	Whiten the series z = Vx
	#
	seriesC = seriesC.apply(lambda row: np.dot(V, row.T).T, axis=1)
	return seriesC

