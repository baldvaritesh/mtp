import whitening as wt
import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
import sklearn
from sklearn import linear_model
import statsmodels.tsa.stattools as st
import statsmodels.tsa.api as st2

# Data Types
PRICE = 7
ARRIVAL = 2
PRICE_CENTRE = 2

c = wt.c
m = wt.m

def getChosenMandisAverage(c, m, centreIndex, dataType):
	l = len(m[centreIndex])
	mandis = m[centreIndex][0].copy()
	mandis[0] = mandis[dataType]
	del mandis[dataType]
	for i in xrange(1, l):
		mandis[i] = m[centreIndex][i][dataType]
	mandis[l] = mandis.apply(lambda row: sum(row)/l, axis=1)
	return mandis

def getDataForVAR(c,m,centreIndex, dataType):
	l = len(m[centreIndex])
	data = c[centreIndex].copy()
	data[0] = data[PRICE_CENTRE]
	del data[PRICE_CENTRE]
	for i in xrange(0, len(m[centreIndex])):
		data[i+1] = m[centreIndex][i][dataType]
	return data

def MADThreshold(array):
	median = np.median(array)
	diff = []
	for i in range(0,len(array)):
	    diff.append(abs(median - array[i]))
	median_of_diff = np.median(np.array(diff))
	tolerance = 1.4826 * median_of_diff
	return (median - tolerance,median + tolerance)	

# Window Correlation Analysis
def WindowCorrelation(c, m, centreIndex, window=15):
	mandis = getChosenMandisAverage(c, m, 0, PRICE)
	corrs = []
	l1 = len(m[centreIndex])
	l2 = len(mandis[l1])
	for i in xrange(0, l2 - window + 1):
		corr = st.ccf( c[centreIndex][PRICE_CENTRE][i: (i + window)] , mandis[l1][i: (i + window)], unbiased=True)
		corrs.append(corr[0])
	anom = []
	(lower_threshold, upper_threshold) = MADThreshold(corrs)
	idx = pd.date_range('2006-01-01', '2015-06-23')
	for i in xrange(0, len(corrs)):
		if(corrs[i] < lower_threshold or corrs[i]  > upper_threshold):
			anom.append(idx[i])
	return anom


# Multivariate Analysis Anomalies
def MVARAnalysis(c, m, centreIndex, maxlgs=15):
	data = getDataForVAR(c,m,centreIndex, PRICE)
	l = len(data)
	trainIdx = int(0.8 * l)
	dataTrain = data.head(trainIdx)
	dataTest = data.tail(l - trainIdx)
	model = st2.VAR(dataTrain)
	results = model.fit()
	initialValue = data[0][trainIdx]
	forecastValues = results.forecast(dataTest.values, l - trainIdx)
	diff = dataTest.values
	for i in xrange(l - trainIdx):
		for j in xrange(0, len(m[centreIndex]) + 1):
			diff[i][j] = abs(forecastValues[i][j] - diff[i][j])
	idx = pd.date_range('2006-01-01', '2015-06-23')
	(lower_threshold, upper_threshold) = MADThreshold(diff.T[0])
	anom = []
	for i in xrange(l - trainIdx):
		if(diff[i][0] < lower_threshold or diff[i][0] > upper_threshold):
			anom.append(idx[i + trainIdx])
	return anom 

# Linear Regression Anomalies
def LinearRegression(c, m, centreIndex):
	mandis = getChosenMandisAverage(c, m, 0, PRICE)
	xSeries = np.array(c[centreIndex][PRICE_CENTRE].tolist())
	ySeries = np.array(mandis[len(m[centreIndex])].tolist())
	xSeries = xSeries.reshape(len(xSeries),1)
	ySeries = ySeries.reshape(len(ySeries),1)
	regr = linear_model.LinearRegression()
	trainIdx = int(0.8 * len(c[PRICE_CENTRE]))
	xSeriesTrain = xSeries[:trainIdx]
	ySeriesTrain = ySeries[:trainIdx]
	xSeriesTest = xSeries[trainIdx:]
	ySeriesTest = ySeries[trainIdx:]
	regr.fit(xSeriesTrain, ySeriesTrain)
	diff = []
	predictedValue = regr.predict(xSeriesTest)
	for i in xrange(len(xSeriesTest)):
		diff.append(abs(ySeriesTest[i][0] - predictedValue[i][0]))
	(lower_threshold, upper_threshold) = MADThreshold(diff)
	idx = pd.date_range('2006-01-01', '2015-06-23')
	anom = []
	for i in xrange(0, len(diff)):
		if(diff[i] < lower_threshold or diff[i] > upper_threshold):
			anom.append(idx[i + trainIdx])
	return anom