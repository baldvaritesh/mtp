from bottle import get, post, request, run, response,template,redirect # or route
import numpy as np
import datetime
from slopeBasedDetection import *
from Utility import *
from window_correlation import anomaliesFromWindowCorrelationWithConstantlag
from slopeBasedDetection import slopeBasedDetection, anomalyDatesSlopeBaseddetetion
from linear_regression import linear_regression, anomalies_from_linear_regression

ResList= dict()
CsvRelations=[]
CSVcount=0

@get('/home') # or @route('/login')
def home():
    return '''
        <form action="/home" method="post">
            Number Of CSVs: <input name="noOfCSVs" type="text" />
            <input value="Submit" type="submit" />
        </form>
    '''

@post('/home') # or @route('/login', method='POST')
def do_home():
    noOfCSVs = request.forms.get('noOfCSVs')
    global CSVcount
    CSVcount=int(noOfCSVs)
    if noOfCSVs.isdigit():
        return template('CSVInputTemplate', csvCount=int(noOfCSVs))
    else:
        return "<p>Invalid Number.</p>"+str(noOfCSVs)

@get('/inputCSVs')
def inputCSVs():
    return "Finally"

@post('/inputCSVs')
def do_inputCSVs():
    global ResList
    for filename, file in request.files.iteritems():
    	Con = request.files[filename].name
	z=processFile(request.files.get(Con).file.readlines())
	ResList[Con] = formatCSV2Array(z)
    redirect("/relationEntry")

@get('/relationEntry') # or @route('/login')
def relationEntry():
    return template('CSVRelationEntry', csvCount=CSVcount,resList= ResList)

@post('/relationEntry') # or @route('/login')
def do_relationEntry():
    global CsvRelations
    for i in range(CSVcount):
	temp=[]
	for j in range(CSVcount):
		val=request.forms.get(str(i+1)+"_"+str(j+1))
		temp.append(int(val))
	CsvRelations.append(temp)
    resultString = hypothesisTesting()
    return resultString
    #return printCSVAsList(CsvRelations)

def ExponentialSmoothData(csvList):
	dateofdata= [i[0] for i in csvList]
	array= [i[1] for i in csvList]
	s_date=dateofdata[0]
        end_date=dateofdata[-1]
	return smoothArray(s_date,dateofdata, array, end_date)

def smoothArray(s_date,dateofdata, array, end_date,alpha = 2.0/15.0):
    array = np.array(array,dtype = float)
    start_date = s_date
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    #return str(start_date) + " " + str(end_date)

    new_data = []
    prevVal = -1
    i=0 # To keep track over the arrays passed
    while(start_date <= end_date):
    	dateofdata[i] = datetime.datetime.strptime(str(dateofdata[i]), "%Y-%m-%d").date()
        if(start_date == dateofdata[i]):
            # data for this date is present
            if(i==0):
                # Simply add to final array
                prevVal = array[i]
                new_data.append([start_date,array[i]])                
            else:
                # Smooth
                if(prevVal == -1):
                    #print " preval == -1 "
                    prevVal = array[i]
                    new_data.append([start_date,array[i]])
                else:
                    newVal = ( array[i] - prevVal ) * alpha + prevVal
                    new_data.append([start_date,newVal])
                    prevVal = newVal
            start_date = start_date + datetime.timedelta(days=1)
            i = i+1 
        else:
            # Data for this date is missing
            if(prevVal == -1):
                new_data.append([start_date,array[i]])
            else:
                new_data.append([start_date,prevVal])            
            start_date = start_date + datetime.timedelta(days=1)    
    return str(new_data)

def printCSVAsList(csvList):
    te=""
    for x in csvList:
	for y in x:
		te=te+str(y)#str(y[0])+str(y[1])
	te = te + "\n"
    return te	

def processFile(csvFile):
	listOfData=[]
	for line in csvFile:
		listOfData.append(((line.split(',')[0]).strip(),(line.split(',')[1]).strip()))
	return listOfData


def hypothesisTesting():
	for i in range(0,CSVcount):
		for j in range(0,CSVcount):
			csv1_name = "CSV" + str(i+1)
			csv2_name = "CSV" + str(j+1)
			csv1 = ResList[csv1_name]
			csv2 = ResList[csv2_name]
			relation = CsvRelations[i][j]
			
			if(relation == 0):
				pass
			elif(relation == -1):
			# Hypothesis 1
				pass
			elif(relation == 2):
				pass
			elif(relation == 1):
				# Hypothesis 2
				# Correlation Results
				anomalies_from_correlation = anomaliesFromWindowCorrelationWithConstantlag(csv1, csv2, window_size=15,maxlag=15, positive_correlation=True, pos=1, neg=1)
				# Slope Based Detection Technique
				# Extracting only data
				data1 = [x[1] for x in csv1]
				data2 = [x[1] for x in csv2]
				slope_based = slopeBasedDetection(data1,False,data2,False)
				anomalies_from_slope_based = anomalyDatesSlopeBaseddetetion(slope_based,csv1)
				(lr_based,lr_object) = linear_regression(data1, data2, 1)
				anomalies_from_lr = anomalies_from_linear_regression(lr_based,csv1)
				
				# Converting results to string
				resultString = ""
				resultString = "Anomalies from Correlation test <br>"
				resultString += "Start Date &nbsp;&nbsp;&nbsp;&nbsp; End Date &nbsp;&nbsp;&nbsp;&nbsp; Correlation Value<br>"
				for dataPoint in anomalies_from_correlation:
					resultString += str(dataPoint[0]) + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[1]) + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[2]) + "<br>"
				resultString += "Anomalies from Slope Based test <br>"
				resultString += "Start Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; End Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Slope Value <br>"
				for dataPoint in anomalies_from_slope_based:
					resultString += str(dataPoint[0]) + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[1]) + "&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[2]) + "&nbsp;&nbsp;&nbsp;&nbsp; <br>" 
				resultString += "Anomalies from Linear Regression test<br>"
				resultString += "Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; X Val &nbsp;&nbsp;&nbsp;&nbsp; Y Val &nbsp;&nbsp;&nbsp;&nbsp; Expected Y Val &nbsp;&nbsp;&nbsp;&nbsp; Difference <br>"
				for dataPoint in anomalies_from_lr:
					resultString += str(dataPoint[0]) + "&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[1]) + "&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[2]) + "&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[3]) + "&nbsp;&nbsp;&nbsp;&nbsp;" + str(dataPoint[4]) + "<br>" 
				plotGraph(csv1,csv2,anomalies_from_correlation)
				return resultString
			elif(relation == -2):				
				pass
				
	# Hypothesis 1 Methods
	# Correlation
	pass 
	# Hypothesis 2 Methods

run(host='localhost', port=8080, debug=True)
