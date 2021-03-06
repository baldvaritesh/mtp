'''

TODO: DONE : Testing code run fine, to be tested, checked


Handle default_threshold = False case in 

def slopeBasedDetection(series1,smoothed1,series2,smoothed2,next_val_to_consider = 7, default_threshold = True, threshold = 0, what_to_consider = 1):

'''

import numpy
from Utility import MADThreshold 
from Utility import smoothArray
import numpy as np

'''
This function takes 8 arguments:

1. series1 : Array of elements (int, real_vals)
2. smoothed1 : whether series1 is smoothed or not.
3. series2 : Array of elements (int, real_vals)
4. smoothed2 : whether series2 is smoothed or not.
5. next_val_to_consider: Which Val to consider to calculate slope? Usually next Val, but for our data we take 7 days
6. default_threshold: whether to consider default threshold or not (True/False)
7. threshold: This is threshold value to consider if not default one.
8. what_to_consider :
    1. Only positive slopes
    0. Both type of slopes, positive as well as negative
    -1. Only negative slopes


Note:

When default_threshold = True
    For the case of what_to_consider=1 and what_to_consider=-1, we have two different thresholds.
    For what_to_consider = 1, we consider only postitive slope values and calculate threshold
    For what_to_consider = -1, we consider only negative slope values and calculate threshold
    For what_to_consider = 0, we take union of above of two results.
    
When default_threshold = False
    For what_to_consider = 1, we consider only postitive slope values which are > given threshold
    For what_to_consider = -1, we consider only negative slope values which are < given threshold
    For what_to_consider = 0, we consider those slope values whose absolute value is > given threshold


returns array of tuples as follows:
(first,second,slope_value)
where first and second specifies the points between which slope was calculated. slope_value is the value of slope between those 2 points.

'''

def slopeBasedDetection(series1,smoothed1,series2,smoothed2,next_val_to_consider = 7, default_threshold = True, threshold = 0, what_to_consider = 1):
    if(smoothed1 == False):
        series1 = smoothArray(series1)
    if(smoothed2 == False):
        series2 = smoothArray(series2)
    
    n = len(series1)
    positive_slopes = []
    anomalous_pts = []
    negative_slopes = []
    i = 0
    while(i<(n-next_val_to_consider+1)):
        if((series2[i+next_val_to_consider-1] - series2[i]) == 0):
            i= i+ next_val_to_consider 
            continue
        diff = ((series1[i+next_val_to_consider-1] - series1[i]) * series2[i] )/ ((series2[i+next_val_to_consider-1] - series2[i]) * series1[i])
        if(diff < 0):
            negative_slopes.append((i,i+next_val_to_consider-1,diff))
        else:
            positive_slopes.append((i,i+next_val_to_consider-1,diff))
        i= i+ next_val_to_consider
    
             
    if(default_threshold == True):
        temp = []
        for x in positive_slopes:
            temp.append(x[2])
        if(len(temp)>0):
            (_,positive_threshold) = MADThreshold(temp)
        # print "Positive Threshold Value:" + str(positive_threshold)
        
    if(default_threshold == True):
        temp = []
        for x in negative_slopes:
            temp.append(x[2])
        if(len(temp)>0):
            (negative_threshold,_) = MADThreshold(temp)
        # print "Negative Threshold Value:" + str(negative_threshold)
    
    if(what_to_consider == 1):
        positive_anomalous_pts = []        
        if(default_threshold):
            print "Possitive Threshold of Slope Based : " + str(positive_threshold)
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > positive_threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
        else:
            print "Possitive Threshold of Slope Based User Given: " + str(threshold)
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
        return positive_anomalous_pts
    elif(what_to_consider == -1):        
        negative_anomalous_pts = []
        if(default_threshold):
            print "Negative Threshold of Slope Based : " + str(negative_threshold)
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < negative_threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
        else:
            print "Negative Threshold of Slope Based User Given: " + str(threshold)
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
        return negative_anomalous_pts
    elif(what_to_consider == 0):
        if(default_threshold):
            print "Possitive Threshold of Slope Based : " + str(positive_threshold)
            print "Negative Threshold of Slope Based : " + str(negative_threshold)
            positive_anomalous_pts = []
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > positive_threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
            negative_anomalous_pts = []
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < negative_threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
            anomalous_pts = positive_anomalous_pts  + negative_anomalous_pts
            # Sort array according to start of window
            sorted(anomalous_pts, key=lambda x: x[0])    
            return anomalous_pts
        else:
            print "Threshold of Slope Based User Given: " + str(threshold)
            positive_anomalous_pts = []
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
            negative_anomalous_pts = []
            for i in range(0,len(negative_slopes)):
                if(abs(negative_slopes[i][2]) > threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
            anomalous_pts = positive_anomalous_pts  + negative_anomalous_pts
            # Sort array according to start of window
            sorted(anomalous_pts, key=lambda x: x[0])    
            return anomalous_pts
    pass

'''
This function takes 2 arguments:

slopeBasedResult: Result of function "slopeBasedDetection"
any_series: Any CSV in the format of 2 columns (Date,Value), date will be used

Returns array of tuples of the form (start_date,end_date,slope_value)

'''
def anomalyDatesSlopeBaseddetetion(slopeBasedResult,any_series):
    result = []
    for i in range(0,len(slopeBasedResult)):
        start_date = any_series[slopeBasedResult[i][0]][0]
        end_date = any_series[slopeBasedResult[i][1]][0]
        result.append((start_date,end_date,slopeBasedResult[i][2]))
    return result

'''

This is MAIN Function of this method.

This function takes 8 arguments:

1. series1 : Array of elements (date, real_vals)
2. smoothed1 : whether series1 is smoothed or not.
3. series2 : Array of elements (date, real_vals)
4. smoothed2 : whether series2 is smoothed or not.
5. next_val_to_consider: Which Val to consider to calculate slope? Usually next Val, but for our data we take 7 days
6. default_threshold: whether to consider default threshold or not (True/False)
7. threshold: This is threshold value to consider if not default one.
8. what_to_consider :
    1. Only positive slopes
    0. Both type of slopes
    -1. Only negative slopes


Returns array of tuples of the form (start_date,end_date,slope_value)


'''
def slopeBased(series1,smoothed1,series2,smoothed2,next_val_to_consider = 7, default_threshold = True, threshold = 0, what_to_consider = 1):
    # Extract just values from the series
    # First column is date and second is value
    series1_vals = [ row[1] for row in series1]
    series2_vals = [ row[1] for row in series2]
    result_1 = slopeBasedDetection(series1_vals,smoothed1,series2_vals,smoothed2,next_val_to_consider, default_threshold, threshold, what_to_consider)
    return anomalyDatesSlopeBaseddetetion(result_1,series1)



def temp(series1,smoothed1,series2,smoothed2,next_val_to_consider = 7, default_threshold = True, threshold = 0, what_to_consider = 1):
    if(smoothed1 == False):
        series1 = smoothArray(series1)
    if(smoothed2 == False):
        series2 = smoothArray(series2)
    
    n = len(series1)
    negative_slopes = []
    positive_slopes = []
    anomalous_pts = []
    i = 0
    while(i<(n-next_val_to_consider+1)):
        if((series2[i+next_val_to_consider-1] - series2[i]) == 0):
            i= i+ next_val_to_consider 
            continue
        diff = ((series1[i+next_val_to_consider-1] - series1[i]) * series2[i] )/ ((series2[i+next_val_to_consider-1] - series2[i]) * series1[i])
        if(diff < 0):
            negative_slopes.append((i,i+next_val_to_consider-1,diff))
        else:
            positive_slopes.append((i,i+next_val_to_consider-1,diff))
        i= i+ next_val_to_consider
    
    print "Length of positive slopes:" + str(len(positive_slopes))
    print "Length of negative slopes:" + str(len(negative_slopes))
        
    if(default_threshold == True):
        temp = []
        for x in positive_slopes:
            temp.append(x[2])
        if(len(temp)>0):
            (_,positive_threshold) = MADThreshold(temp)
        # print "Positive Threshold Value:" + str(positive_threshold)
        
    if(default_threshold == True):
        temp = []
        for x in negative_slopes:
            temp.append(x[2])
        if(len(temp)>0):
            (negative_threshold,_) = MADThreshold(temp)
        # print "Negative Threshold Value:" + str(negative_threshold)
    
    if(what_to_consider == 1):
        positive_anomalous_pts = []
        if(default_threshold):
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > positive_threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
        else:
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
        # return positive_anomalous_pts
        print "Threshold Value is:" + str(positive_threshold)
        anomalous_pts = positive_slopes  + negative_slopes
        # Sort array according to start of window
        sorted(anomalous_pts, key=lambda x: x[0])    
        return anomalous_pts
    elif(what_to_consider == -1):
        negative_anomalous_pts = []
        if(default_threshold):
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < negative_threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
        else:
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
        return negative_anomalous_pts
    elif(what_to_consider == 0):
        if(default_threshold):
            positive_anomalous_pts = []
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > positive_threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
            negative_anomalous_pts = []
            for i in range(0,len(negative_slopes)):
                if(negative_slopes[i][2] < negative_threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
            anomalous_pts = positive_anomalous_pts  + negative_anomalous_pts
            # Sort array according to start of window
            sorted(anomalous_pts, key=lambda x: x[0])    
            return anomalous_pts
        else:
            positive_anomalous_pts = []
            for i in range(0,len(positive_slopes)):
                if(positive_slopes[i][2] > threshold):
                    positive_anomalous_pts.append(positive_slopes[i])
            negative_anomalous_pts = []
            for i in range(0,len(negative_slopes)):
                if(abs(negative_slopes[i][2]) > threshold):
                    negative_anomalous_pts.append(negative_slopes[i])
            anomalous_pts = positive_anomalous_pts  + negative_anomalous_pts
            # Sort array according to start of window
            sorted(anomalous_pts, key=lambda x: x[0])    
            return anomalous_pts
        
def temp1234(series1,smoothed1,series2,smoothed2,next_val_to_consider = 7, default_threshold = True, threshold = 0, what_to_consider = 1):
    # Extract just values from the series
    # First column is date and second is value
    series1_vals = [ row[1] for row in series1]
    series2_vals = [ row[1] for row in series2]
    result_1 = temp(series1_vals,smoothed1,series2_vals,smoothed2,next_val_to_consider, default_threshold, threshold, what_to_consider)
    x =  anomalyDatesSlopeBaseddetetion(result_1,series1)
    for i in range(0,len(x)):
        slope = x[i][2]
        start_date = x[i][0]
        end_date = x[i][1]
        print str(start_date) + "," + str(end_date) + "," + str(slope)
        
        
##########################################################################
##########          TESTING CODE            ##############################
##########################################################################
'''
from Utility import csv2array


wholesale = csv2array('/home/kapil/Desktop/project/library/MumbaiWholesalePriceSmoothed.csv')
retail = csv2array('/home/kapil/Desktop/project/library/MumbaiRetailPriceSmoothed.csv')
wholesale_price = []
retail_price = []
for x in wholesale:
    wholesale_price.append(float(x[1]))

for x in retail:
    retail_price.append(float(x[1]))

anomalies = slopeBasedDetection(wholesale_price,True,retail_price,True,7,True,0,1)

for i in range(0,len(anomalies)):
    start_index = anomalies[i][0]
    end_index = anomalies[i][1]
    slope = anomalies[i][2]
    start_date = wholesale[start_index][0]
    end_date = wholesale[end_index][0]
    print str(start_date) + "," + str(end_date) + "," + str(slope)
'''