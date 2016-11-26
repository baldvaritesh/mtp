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

def getOtherCentresAverage(c, centreIndex, dataType):
	l = len(c)
	centres = c[centreIndex].copy()
	centres[l] = centres[PRICE_CENTRE]
	del centres[PRICE_CENTRE]
	idx = [0,1,2,3,4]
	idx.remove(centreIndex)
	for i in xrange(len(idx)):
		centres[i] = c[idx[i]][PRICE_CENTRE]
	centres[l] = centres.apply(lambda row: (sum(row) - row[l])/(l-1), axis=1)
	return centres

def getDataForVAR(c,m,centreIndex, dataType):
	l = len(m[centreIndex])
	data = c[centreIndex].copy()
	data[0] = data[PRICE_CENTRE]
	del data[PRICE_CENTRE]
	for i in xrange(0, len(m[centreIndex])):
		data[i+1] = m[centreIndex][i][dataType]
	return data

def getDataForVAR2(c):
	l = len(c)
	data = c[0].copy()
	data[0] = data[PRICE_CENTRE]
	del data[PRICE_CENTRE]
	for i in xrange(1, l):
		data[i] = c[i][PRICE_CENTRE]
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


def WindowCorrelation2(c, centreIndex, window=15):
	centres = getOtherCentresAverage(c, centreIndex, PRICE_CENTRE)
	corrs = []
	l1 = len(c)
	l2 = len(centres[l1])
	for i in xrange(0, l2 - window + 1):
		corr = st.ccf( c[centreIndex][PRICE_CENTRE][i: (i + window)] , centres[l1][i: (i + window)], unbiased=True)
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

def MVARAnalysis2(c, centreIndex, maxlgs=15):
	data = getDataForVAR2(c)
	l = len(data)
	trainIdx = int(0.8 * l)
	dataTrain = data.head(trainIdx)
	dataTest = data.tail(l - trainIdx)
	model = st2.VAR(dataTrain)
	results = model.fit()
	initialValue = data[centreIndex][trainIdx]
	forecastValues = results.forecast(dataTest.values, l - trainIdx)
	diff = dataTest.values
	for i in xrange(l - trainIdx):
		for j in xrange(0, len(c)):
			diff[i][j] = abs(forecastValues[i][j] - diff[i][j])
	idx = pd.date_range('2006-01-01', '2015-06-23')
	(lower_threshold, upper_threshold) = MADThreshold(diff.T[centreIndex])
	anom = []
	for i in xrange(l - trainIdx):
		if(diff[i][0] < lower_threshold or diff[i][0] > upper_threshold):
			anom.append(idx[i + trainIdx])
	return anom 

# Linear Regression Anomalies
def LinearRegression(c, m, centreIndex):
	mandis = getChosenMandisAverage(c, m, centreIndex, PRICE)
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

def LinearRegression2(c, centreIndex):
	centres = getOtherCentresAverage(c, centreIndex, PRICE_CENTRE)
	xSeries = np.array(c[centreIndex][PRICE_CENTRE].tolist())
	ySeries = np.array(centres[len(c)].tolist())
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