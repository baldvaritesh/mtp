import numpy
import numpy as np
import csv
import matplotlib.pyplot as plt
import datetime
import StringIO
import plotly
from plotly.graph_objs import Scatter, Layout
import plotly.plotly as py
import plotly.graph_objs as go
from bottle import route, run, debug, template, request, static_file, error, get, post, response,  static_file, view
import plotly.plotly as py
py.sign_in('mcs142124', 'p7p80472qt')
from datetime import date
from datetime import datetime
from datetime import timedelta

'''
This function takes one argument:
array: Array of integers, real numbers, etc

returns threshold value to be consider using MAD Test
'''
def MADThreshold(array):
    # return 1.4826*numpy.median(np.array(array))
    array = np.array(array)
    median = numpy.median(array)
    diff = []
    for i in range(0,len(array)):
        diff.append(abs(median - array[i]))
    median_of_diff = numpy.median(np.array(diff))
    tolerance = 1.4826 * median_of_diff
    return (median - tolerance,median + tolerance)
    

'''
This function takes 2 arguments:
array: Array of integers, real numbers, etc
alpha: smoothening factor of exponential average smoothing

returns threshold value to be consider using MAD Test
'''
def smoothArray(array, alpha = 2.0/15.0):
    array = np.array(array,dtype = float)
    if(len(array) == 0):
        return []
    new_data = []
    prevVal = -1
    prevVal = array[0]
    new_data.append(array[0])
    for i in range(1,len(array)):
        newVal = ( array[i] - prevVal ) * alpha + prevVal
        new_data.append(newVal)
        prevVal = newVal   
    return new_data

def csv2array(filePath):
    result = []
    with open(filePath, 'rb') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            result.append(row)
    return result

def getColumn(array, column_number):
    temp = []
    for x in array:
        temp.append(x[column_number])
    return temp

'''
While reading CSV file, by default it takes each row as string, but second column should be float, so this function does that work.

1 Argument:

z : Array from CSV file consisting of 2 columns, date and values
return same array changing data type of second column to float

'''
def formatCSV2Array(z):
    result = []
    for row in z:
        result.append((row[0],float(row[1])))
    return result

def plotGraph(series1,series2,anomalies):
    dates = [datetime.datetime.strptime(x[0], "%Y-%m-%d").date() for x in series1]
    s1 = [x[1] for x in series1]
    s2 = [x[1] for x in series2]
    html = '''
    <html>
        <body>
            <img src="data:image/png;base64,{}"  height="800" width="1100"/>
        </body>
    </html>
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(dates,s1,'r')
    ax.plot(dates,s2,'b')
    
    # Highlighting Anomalies
    for i in range(0,len(anomalies)):
        # ax.axvspan(datetime.datetime.strptime(anomalies[i][0], "%Y-%m-%d").date(), datetime.datetime.strptime(anomalies[i][1], "%Y-%m-%d").date(), color='y', alpha=0.5, lw=0)
        ax.axvspan(anomalies[i][0], anomalies[i][1], color='y', alpha=0.5, lw=0)
    
    
    fig.set_size_inches(20,12)
    plt.show()
    io = StringIO.StringIO()
    fig.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    
    trace1 = go.Scatter(
    x=dates,
    y=s1,
    name='Series 1'
    )
    trace2 = go.Scatter(
        x=dates,
        y=s2,
        name='Series 2',
        yaxis='y2'
    )
    data = [trace1, trace2]
    layout = go.Layout(
        title='Correlation Test',
        yaxis=dict(
            title='Series 1'
        ),
        yaxis2=dict(
            title='Series 2',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        )
    )
    fig = go.Figure(data=data, layout=layout)
    # plot_url = plotly.offline.plot(fig, filename='graph1', auto_open=False)
    temp = plotly.offline.plot( fig, filename='graph1')
    print "Kapil"
    print temp
    return template('graphPlot', graph=temp)

'''

This function takes one argument:

li: List of tuples of the forms as follows:

(start_date, end_date, value)


It merges windows if it overlaps.

returns list of tuples of the form:

(start_date, end_date, value)

'''
def mergeDates(li):
    # Convert first and second item of tuple to date from string
    # print li
    li = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c) for (a,b,c) in li]
    li = sorted(li, key=lambda x: x[0]) # sort input list
    new_list_of_ranges = [] # output list
    
    new_range_item_start = None
    new_range_item_end = None
    new_value = None
    
    length = len(li)
    for i,range_item in enumerate(li):
        if new_range_item_start is None:
            new_range_item_start = range_item[0]
            new_range_item_end = range_item[1]
            new_value = range_item[2]
        #elif new_range_item_end >= range_item[0]:
        elif((abs(new_range_item_end- range_item[0]).days) == 1):
            new_range_item_end = max(range_item[1], new_range_item_end)
            new_value = max(new_value, range_item[2])
        else:
            new_list_of_ranges.append((new_range_item_start, new_range_item_end, new_value))
            new_range_item_start = range_item[0]
            new_range_item_end = range_item[1]
            new_value = range_item[2]
        # save if this is last item
        if i + 1 == length:
            new_list_of_ranges.append((new_range_item_start, new_range_item_end, new_value))
    return new_list_of_ranges


'''

This function requires minumum 5 arguments:

numOfResults: number of lists you are passing, minimum 2

listi : result from ith alorithm : list
resultOfi : result of which algorithm : string, it can be from following:
            (slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

It finds intersection of all algos.

returns list of tuples.

Return Tuple format:

(date, correlation, slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

'''
def intersection(numOfResults, list1, resultOf1, list2, resultOf2, list3 = [], resultOf3="linear_regression", list4=[], resultOf4="graph_based", list5=[], resultOf5="spike_detection" , list6=[], resultOf6="multiple_arima"):
    # Convert first and second item of tuple to date from string
    # First Combine both the results into one, 3 tuples to 4 tuples -> 4th will be from which time series it is.
    '''
    li1 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf1) for (a,b,c) in list1]
    li2 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf2) for (a,b,c) in list2]
    li3 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf3) for (a,b,c) in list3]
    li4 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf4) for (a,b,c) in list4]
    li5 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf5) for (a,b,c) in list5]
    li6 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf6) for (a,b,c) in list6]
    '''
    
    li1 = [ (a,b,c, resultOf1) for (a,b,c) in list1]
    li2 = [ (a,b,c, resultOf2) for (a,b,c) in list2]
    li3 = [ (a,b,c, resultOf3) for (a,b,c) in list3]
    li4 = [ (a,b,c, resultOf4) for (a,b,c) in list4]
    li5 = [ (a,b,c, resultOf5) for (a,b,c) in list5]
    li6 = [ (a,b,c, resultOf6) for (a,b,c) in list6]
    
    # Append one list to other
    list = li1 + li2 + li3 + li4 + li5 + li6

    temp = dict()

    for (a,b,c,d) in list:
        i = a
        while i <= b:
            # for i in range(a,b+timedelta(days = 1)):
            if(i in temp):
                temp[i] = temp[i] + 1
            else:
                temp[i] = 1
            i = i + timedelta(days = 1)

    dates_to_consider = set()
    for i in temp:
        if(temp[i] == numOfResults):
            dates_to_consider.add(i)

    # Fetch data
    results = dict()
    for (a,b,c,d) in list:
        i = a
        while i <= b:
            # for i in range(a,b+timedelta(days = 1)):
            if(i in dates_to_consider):
                if(i in results):
                    previous_tuple = results[i]
                else:
                    previous_tuple = [i,0,0,0,0,0,0]
                if(d == "correlation"):
                    previous_tuple[1] = c
                elif(d== "slope_based"):
                    previous_tuple[2] = c
                elif(d== "linear_regression"):
                    previous_tuple[3] = c
                elif(d== "graph_based"):
                    previous_tuple[4] = c
                elif(d== "spike_detection"):
                    previous_tuple[5] = c
                elif(d== "multiple_arima"):
                    previous_tuple[6] = c
                results[i] = previous_tuple
            i = i + timedelta(days = 1)


    # output list
    new_list_of_ranges = [] 
    for i in results:
        new_list_of_ranges.append(results[i])

    #Sort it
    new_list_of_ranges = sorted(new_list_of_ranges, key=lambda x: x[0])

    return new_list_of_ranges