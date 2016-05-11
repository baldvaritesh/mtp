import numpy
import math
import matplotlib.pyplot as plt
import scipy.stats
from Utility import MADThreshold 
import datetime
import numpy as np

'''
This function takes 5 arguments:
arr1: Series 1
arr2: Series 2
maxlag: maximum lag to consider
pos: to take potitive lag or not, i.e. 1 to maxlag
neg: to take negative lag or not, i.e. -maxlag to -1

Returns an array containing tuples of the form (lag, correlation at this lag)

Requirements: Length of both the series should be equal
'''
def correlation(arr1, arr2, maxlag, pos=1, neg=1):
    # Will contain tuples (lag, correlation)
    result = []
    
    # Checking for requirements
    if(len(arr1) != len(arr2)):
        print "Error! In Function: correlation(arr1, arr2, maxlag, pos=1, neg=1): \n Length of the both series should be same. Returning empty result. \n"
        return result
    
    # Mean of the two series
    # print arr1
    arr1  = np.array(arr1).astype(np.float)
    arr2  = np.array(arr2).astype(np.float)
    mean1 = numpy.mean(arr1)
    mean2 = numpy.mean(arr2)
    
    # Calculating the denominator
    sx = 0
    sy = 0
    for i in range(0,len(arr1)):
        sx += (arr1[i] - mean1) * (arr1[i] - mean1)
        sy += (arr2[i] - mean2) * (arr2[i] - mean2)
    denom  = math.sqrt(sx * sy)
    
    # Getting max and min lag
    maxLag = maxlag         # Default: Both sides are to be considered
    minLag = -maxlag
    if(pos==1 and neg ==0):
        minLag = 0
    elif(pos==0 and neg ==1):
        maxlag = 0
    
    # Calculate correlation at multiple lags
    lag = 0
    for lag in range(minLag,maxlag+1):
        sxy = 0
        for i in range(0,len(arr1)):
            j = i + lag
            if(j<0 or j>= len(arr1)):
                continue
            else:
                sxy += (arr1[i] - mean1) * (arr2[j] - mean2)
        r = sxy / denom
        result.append((lag,r))
        
    return result

'''
This function takes 2 arguments:
arr1: Series of the form (lag,correlation)
positive_correlation: true if we are looking for maximum positive correlation, else false

Returns a tuple of the form (lag,correlation), where correlation value is the maximum or minimum of the array depending on positive_correlation parameter.
Lag is the lag value at which we found max/min correlation value
'''
def getMaxCorr(arar1,positive_correlation):
    if(positive_correlation == True):
        (maxLag,corr) = arar1[0]
        for (lag, correlation) in arar1:
            if(corr < correlation):
                (maxLag,corr) = (lag, correlation)
        return (maxLag,corr)
    else:
        (minLag,corr) = arar1[0]
        for (lag, correlation) in arar1:
            if(corr > correlation):
                (minLag,corr) = (lag, correlation)
        return (minLag,corr)

'''
This function takes 7 arguments:
arr1: Series 1
arr2: Series 2
maxlag: maximum lag to consider
positive_correlation: true if we are looking for maximum positive correlation, else false
pos: to take potitive lag or not, i.e. 1 to maxlag
neg: to take negative lag or not, i.e. -maxlag to -1
window_size: window size to consider while calculating sliding window correlation

Returns an array containing tuples of the form (lag, max/min correlation at this window) for all windows.
Note that window number can easily be implied by the index of that tuple in resultant array.

Requirements: Length of both the series should be equal
'''
def window_correlation(arr1, arr2, maxlag,window_size=15, positive_correlation=True , pos=1, neg=1):    
    # Will contain tuples (lag, correlation)
    result = []
    
    # Checking for requirements
    if(len(arr1) != len(arr2)):                            
        print "Error! In Function: correlation(arr1, arr2, maxlag, pos=1, neg=1): \n Length of the both series should be same. Returning empty result. \n"
        return result
    
    # Length of array
    n = len(arr1)
    #windows_processed = 0
    if(window_size >= n):
        temp = correlation(arr1,arr2,maxlag,pos,neg)
        # Get maximum correlation
        result.append(getMaxCorr(temp,positive_correlation))
    else:
        for i in range(0,n-window_size):
            # Take out one window and find correlation
            temp_arr_1 = arr1[i:(i+window_size)]
            temp_arr_2 = arr2[i:(i+window_size)]
            temp = correlation(temp_arr_1,temp_arr_2,maxlag,pos,neg)
            # Get maximum correlation and append it to array
            result.append(getMaxCorr(temp,positive_correlation))
            #windows_processed = windows_processed + 1
            #if(windows_processed % 100 == 0):
            #    print windows_processed
    return result

'''
arr: array of tuples of the form (lag,correlation) for each window.

Number of windows = size of an array

Plots correlation at each window
'''
def plotWindowCorr(arr):
    # Extract Correlation values of each window
    y_vals = [x[1] for x in arr]
    # x_vals is nothing but window number
    x_vals = list(xrange(1,len(arr)+1))
    plt.plot(x_vals,y_vals)    
    plt.show()

'''
This function takes 4 arguments:
series1: Series 1
series2: Series 2
maxlag: lag at which correlation is to be calculated for all windows
window_size: window size to consider while calculating sliding window correlation

Returns an array containing correlation values for all windows calculated at given lag.
Note that window number can easily be implied by the index of that tuple in resultant array.

'''
def correlationAtLag(series1, series2, lag, window_size):
    start1 = 0
    start2 = 0
    if(lag>=0):
        start2 = lag
        n2 = len(series2) - lag
        n1 = len(series1)
    else:
        start1 = abs(lag)
        n1 = len(series1) - start1
        n2 = len(series2)
    
    n = min(n1,n2)    
    # Find Correlation at all Window
    result = []
    if(window_size >= n):
        temp = scipy.stats.pearsonr(series1[start1:n],series2[start2:n])
        result.append(temp[0])
    else:
        i= 0
        while(True):
            # Take out one window and find correlation
            j = i + start1
            k = i + start2
            if((j+window_size) >=n or (k+window_size) >=n):
                break
            # print "i:" + str(i)
            # print "j:" + str(j)
            # print "k:" + str(k)
            # print "n:" + str(n)
            # print "\n"
            temp_arr_1 = series1[j:(j+window_size)]
            temp_arr_2 = series2[k:(k+window_size)]
            temp = scipy.stats.pearsonr(temp_arr_1,temp_arr_2)
            # Get maximum correlation and append it to array
            result.append(temp[0])
            if(temp[0] >=1):
                print "tring tring " + str(i) 
            i = i + window_size
    return result

'''
This function takes 7 arguments:
arr1: Series 1
arr2: Series 2
maxlag: maximum lag to consider
positive_correlation: true if we are looking for maximum positive correlation, else false
pos: to take potitive lag or not, i.e. 1 to maxlag
neg: to take negative lag or not, i.e. -maxlag to -1
window_size: window size to consider while calculating sliding window correlation

Returns tuple of the form (lag,array)
Where lag is lag value for which whole series is shifted and then at that lag, we have calculated
correlation for all window. Correlation value for all windows is stored in array.

Requirements: Length of both the series should be equal
'''
def WindowCorrelationWithConstantLag(arr1, arr2, window_size=15,maxlag=15, positive_correlation=True, pos=1, neg=1):
    result1 = correlation(arr1,arr2, maxlag, pos, neg)
    (lag,correlationVal) = getMaxCorr(result1,positive_correlation)
    result2 = correlationAtLag(arr1,arr2, lag, window_size)
    return (lag,result2)

'''
This function takes 7 arguments:
arr1: Series 1 (date, value)
arr2: Series 2 (date, value)
maxlag: maximum lag to consider
positive_correlation: true if we are looking for maximum positive correlation, else false
pos: to take potitive lag or not, i.e. 1 to maxlag
neg: to take negative lag or not, i.e. -maxlag to -1
window_size: window size to consider while calculating sliding window correlation

Returns array of tuples of the form (start_date,end_date,correlation_value)

Requirements: Length of both the series should be equal
'''
def anomaliesFromWindowCorrelationWithConstantlag(arr1, arr2, window_size=15,maxlag=15, positive_correlation=True, pos=1, neg=1):
    arr1_data = [x[1] for x in arr1]
    arr2_data = [x[1] for x in arr2]
    arr = WindowCorrelationWithConstantLag(arr1_data,arr2_data,window_size,maxlag,positive_correlation,pos,neg)
    if(arr[1][0] >= 0):
        array_to_consider = arr1
    else:
        array_to_consider = arr2
    datesOfAnomalies = []

    (lower_thresh,upper_thrash)= MADThreshold(arr[1])
    for i in range(0,len(arr[1])):
        if(lower_thresh > arr[1][i]):
            start_date_of_window = datetime.datetime.strptime(array_to_consider[i*window_size][0], "%Y-%m-%d").date()
            end_date_of_window = start_date_of_window + datetime.timedelta(days=window_size)
            datesOfAnomalies.append((start_date_of_window,end_date_of_window, arr[1][i]))
    return datesOfAnomalies


######################################################################
##                       TESTING CODE                               ##
######################################################################
'''
import random

#a = [random.randint(1,100) for _ in range(50)]
#b = [random.randint(1,100) for _ in range(50)]
from Utility import csv2array
wholesale = csv2array('/home/kapil/Desktop/project/library/MumbaiWholesalePriceSmoothed.csv')
retail = csv2array('/home/kapil/Desktop/project/library/MumbaiRetailPriceSmoothed.csv')
wholesale_price = []
retail_price = []
for x in wholesale:
    wholesale_price.append(float(x[1]))

for x in retail:
    retail_price.append(float(x[1]))

# arr = window_correlation(wholesale_price,retail_price,10,30)
window_size = 15
arr = WindowCorrelationWithConstantLag(wholesale_price,retail_price,window_size,15,True,1,0)
if(arr[1][0] >= 0):
    file_to_consider = wholesale
else:
    file_to_consider = retail
datesOfAnomalies = []

(lower_thresh,upper_thrash)= MADThreshold(arr[1])
for i in range(0,len(arr[1])):
    if(lower_thresh > arr[1][i]):
        start_date_of_window = datetime.datetime.strptime(file_to_consider[i*window_size][0], "%Y-%m-%d").date()
        end_date_of_window = start_date_of_window + datetime.timedelta(days=window_size)
        datesOfAnomalies.append((start_date_of_window,end_date_of_window, arr[1][i]))

# plt.hist(arr[1],bins = 50)
# plt.show()

print "Correlation from MAD Test:" + str(lower_thresh)
for record in datesOfAnomalies:
    print str(record[0]) + "," + str(record[1]) + "," + str(record[2])

'''

#for x in arr:
#    print str(x[0]) + "," + str(x[1])


'''
lags = [x[0] for x in arr]

freq_of_lags = dict()

for x in lags:
    if x not in freq_of_lags:
        freq_of_lags[x] = 1
    else:
        freq_of_lags[x] = freq_of_lags[x] +1
        
for x in freq_of_lags:
    print str(x) + ","  + str(freq_of_lags[x])
'''