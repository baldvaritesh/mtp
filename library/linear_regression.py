import numpy
import sklearn
import numpy as np
from sklearn import  linear_model
import matplotlib.pyplot as plt
from scipy.stats import norm
from Utility import MADThreshold
'''
This function takes 5 arguments:
x_series: independent variable
y_series: dependent variable : y = f(x)
param: Defines what to be treated as anomaly depending on its value as follows:
        0: Values going out of range, both with positive and negative error
        1: Values with potitive errors
        -1: Values with negative errors
default_threshold: Whether to use default threshold used by system using MAD test or user defined threshold
threshold: Threshold value if it is used defined and default_threshold is 'False'

returns Following tuple:

(result,regression_object)

    1. returns "results" array of tuples which are anomaly according to linear regression test of following format:
        Tuple:(Index of Data Point,x_value,y_value,predicted_y_value,difference_between_predicted_and_actual_y_value)
        
    2. regression_object which can be used to regenerate predicted values for plotting graphs afterwards
       Format of using: regression_object.predict(x_value)

Requirements: Length of both the series should be equal
'''
def linear_regression(x_series, y_series, param = 0, default_threshold = True, threshold = 0):
    x_series = np.array(x_series)
    y_series = np.array(y_series)
    x_series = x_series.reshape(len(x_series),1)
    y_series = y_series.reshape(len(y_series),1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    # Train the model using the training sets
    regr.fit(x_series, y_series)
    # Plot outputs
    # plt.scatter( x_series, y_series,  color='black')
    # plt.plot(x_series, regr.predict(x_series), color='blue',linewidth=3)
    # plt.xticks(())
    # plt.yticks(())
    # plt.show()
    
    # Array to store differences between original and predicted
    diff = []

    for i in range(0,len(x_series)):
        x = (y_series[i][0] - regr.predict(x_series[i])[0]) / regr.predict(x_series[i])[0] * 100
        temp = (i,x_series[i][0],y_series[i][0],regr.predict(x_series[i])[0],x)
        if(param == 0):
            diff.append(temp)
        elif(param == 1 and x>0):
            diff.append(temp)
        elif(param == -1 and x<0):
            diff.append(temp)
    
    # Finding outliers
    if(default_threshold == True):
        diff_vals = [abs(x[4]) for x in diff]
        (_,outVal)=  MADThreshold(diff_vals)
    else:
        outVal = threshold
    results = []
    for i in range(0,len(diff)):
        if(abs(diff[i][4]) > outVal):
            results.append(diff[i])
    return (results,regr)

'''
This function takes 2 arguments:

result_of_lr: Result of function "linear_regression"
any_series: Any CSV in the format of 2 columns (Date,Value), date will be used

Returns array of tuples of the form (start_date,x_value,y_value,predicted_y_value,difference_between_predicted_and_actual_y_value)

'''
def anomalies_from_linear_regression(result_of_lr, any_series):
    result = []
    for i in range(0,len(result_of_lr)):
        start_date = any_series[result_of_lr[i][0]][0]
        result.append((start_date,result_of_lr[i][1],result_of_lr[i][2],result_of_lr[i][3],result_of_lr[i][4]))
    return result

'''
This function takes 5 arguments:
x_series: independent variable (date, value)
y_series: dependent variable : y = f(x) of the format (date, value)
param: Defines what to be treated as anomaly depending on its value as follows:
        0: Values going out of range, both with positive and negative error
        1: Values with potitive errors
        -1: Values with negative errors
default_threshold: Whether to use default threshold used by system using MAD test or user defined threshold
threshold: Threshold value if it is used defined and default_threshold is 'False'

Returns array of tuples of the form (start_date,x_value,y_value,predicted_y_value,difference_between_predicted_and_actual_y_value)

Requirements: Length of both the series should be equal
'''

def linear_regressionMain(x_series, y_series, param = 0, default_threshold = True, threshold = 0):
    # Extract just values from the series
    # First column is date and second is value
    x_series_vals = [ row[1] for row in x_series]
    y_series_vals = [ row[1] for row in y_series]
    result1 = linear_regression(x_series_vals, y_series_vals, param = 0, default_threshold = True, threshold = 0)
    temp =  anomalies_from_linear_regression(result1[0], x_series)
    temp1 = [ row[0] for row in temp]
    temp2 = [ row[4] for row in temp]
    return zip(temp1,temp1,temp2)
    
    

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
linear_result = linear_regression(wholesale_price,retail_price, 1)

print linear_result[0]
'''