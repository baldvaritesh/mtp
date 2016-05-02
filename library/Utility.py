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