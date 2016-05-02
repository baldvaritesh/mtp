import numpy
from Utility import MADThreshold 
from Utility import smoothArray
import numpy as np

def getColumnFromListOfTuples(lstTuples,i):
    if len(lstTuples) == 0:
        return []
    elif len(lstTuples[0])< i-1 :
        return []
    else:
        return [item[i-1] for item in lstTuples]
    
def findDiffSeries(series1,diffInterval=1):
    series1 = smoothArray(series1)
    diffSeries =[]
    lenSeries=len(series1)
    if (diffInterval>lenSeries):
        print "diffInterval can not be greater than the length of series"
        return
    i=diffInterval
    while(i<lenSeries):
        diffSeries.append((i-diffInterval,i,((series1[i]-series1[i-diffInterval])/series1[i-diffInterval])*100))
        i=i+1
    (N,P) = MADThreshold(diffSeries)
    print "N & P ::::::::"+ str(N)+":::"+ str(P)
    return diffSeries

def slopeCurveBasedDetection(series1,series2,diffInterval=1):
    ser1= getColumnFromListOfTuples(series1,1)
    ser2= getColumnFromListOfTuples(series2,1)
    
    #Find the bast correlation value for both the time series
    maxCorrAt= 7
    
    resSer1= findDiffSeries(ser1,diffInterval)
    resSer2= findDiffSeries(ser2,diffInterval)
    
    if(maxCorrAt>0):
        resSer1= resSer1[maxCorrAt:]
        resSer2= resSer2[:-1*maxCorrAt]
        #resSer2= [(a-maxCorrAt, b-maxCorrAt, d) for a, b, c in resSer2]
    elif (maxCorrAt<0):
        resSer1= resSer1[:-1*maxCorrAt]
        resSer2= resSer2[maxCorrAt:]
        #resSer1= [(a-maxCorrAt, b-maxCorrAt, d) for a, b, c in resSer1]
        
    rs= [x for x in resSer1 if x not in getColumnFromListOfTuples(resSer2,1)]
    return rs

