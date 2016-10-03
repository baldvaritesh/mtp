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

''' get the dummy centre: 50 and two mandis: 279 (0) , 376 (2) '''
c = cp.cs[2]
m = cp.ms[2]

''' Interpolate all the present series '''
c = c.replace('0.0', np.NaN, regex=True)
c = c.interpolate(method='pchip')
c[2][0] = c[2][1]

m = [x.replace('0.0', np.NaN, regex=True) for x in m]
m[0][7][0] = m[0][7][1]
m[2][7][0] = m[2][7][1] = m[2][7][2] = m[2][7][3]

''' Check if any NaNs exist '''
#
#	c.isnull().values.any()
#

def ZeroMean(series, ind):
	mean = series[ind].mean()
	series[ind] -= mean
	return series 

def g(y, p):
	if(p == 1):
		return y*y*y
	return np.tanh(y)

def gprime(y, p):
	if(p == 1):
		return 3*y*y
	return 1/((np.cosh(y)) ** 2)

def PreProcess(seriesC, seriesM):
	seriesC[0] = seriesM[0][7]
	seriesC[1] = seriesM[2][7]
	for i in xrange(0, 3):
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

def normalize(v):
    norm=np.linalg.norm(v)
    if norm==0: 
       return v
    return v/norm

def FindSingleIC(series, p, function, presentICs):
	found = False
	while (True):
		wp = np.random.uniform(0.0,1.0,3)
		i = 0
		while (True):
			dummy = series.apply(lambda row: row*g(np.dot(wp.T, row), function), axis=1)
			dummy2 = series.apply(lambda row: gprime(np.dot(wp.T, row), function), axis=1)
			Edummy =  dummy.mean()
			Edummy2 = dummy2.mean()
			wpdummy = Edummy2*wp
			wpNew = Edummy2 - wpdummy
			for i in xrange(0, p-1):
				wpNew -= np.dot(wpNew.T, presentICs[i]) * presentICs[i]
			wpNew = normalize(wpNew)
			if abs(np.dot(wpNew.T, wp) - 1) < 0.05 :
				found = True
				break
			if(i == 5):
				break
			print str(i) + ' ' + str(np.dot(wpNew, wp.T))
			wp = wpNew			
			i+=1
		if(found == True):
			print '-----------' + str(p) + '----------------'
			print wpNew 
			break		
	return wpNew

def FindAllIC(series, function, m):
	presentICs = []
	for i in xrange(1, m+1):
		ic = FindSingleIC(series, i, function, presentICs)
		presentICs.append(ic)
	print '----------------END-------------------'
	print presentICs
	return presentICs