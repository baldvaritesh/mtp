import subprocess
from datetime import datetime
import csv
from Utility import MADThreshold
from datetime import timedelta

def multivaraiateAnalysis(args):
    command = 'Rscript'
    path2script = '/home/reshma/Desktop/MTP/mtp/library/MultivariateSeriesModified.R'
    
    # Variable number of args in a list
    # 2000 : number of forecast
    # 3 : Number of series in CSV
    # FALSE: if header is present than it is true, else false.
    
    #args = ['/home/kapil/Desktop/mtp/library/testingCSV/MumbaiSILData.csv','FALSE','3']
    
    # Build subprocess command
    cmd = [command, path2script] + args
    
    # check_output will run the command and store to result
    x = subprocess.check_output(cmd, universal_newlines=True)
    
    #dt= datetime.strptime('2010-01-01' , '%Y-%m-%d')
    #dt= datetime.strptime(startDate, '%Y-%m-%d')
    #output = csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/param"+k+".csv",dt)
    #return output


'''
To transform R Script CSV for MultiVariate Time series forecast method
'''
def csvTransform(filePath,startDate):
    with open(filePath, 'rb') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        rowCount=0
        dtVal=datetime.strptime(startDate, '%Y-%m-%d')
        percDiffArray=[]
        for row in csvReader:
            
            if (rowCount==0):
                rowCount=1
                continue
            if(float(row[5])==-1):
                #print "hault"
                break
        
            percDiff=  ((float(row[5])-float(row[1]))/float(row[1]))*100
            percDiffArray.append(percDiff)
        #Call MadThreshold
        #print percDiff
        (N,P) = MADThreshold(percDiffArray)
	
    outputList=[]
    with open(filePath, 'rb') as csvfile: 
    	csvReader = csv.reader(csvfile, delimiter=',')  
    	rowCount=0
    	cnt=0
    	for row in csvReader:
			#print row
			score=0
			#print row
			if (rowCount==0):
				rowCount=1
				continue
			if(float(row[5])==-1):
				#print "hault"
				break
			if(float(row[5])>float(row[3]) or float(row[5])<float(row[2])):
				score= 1
			percDiff=  ((float(row[5])-float(row[1]))/float(row[1]))*100
		
			if(percDiff>P or percDiff< N):
				if(score==1):
					score=3
				else:
					score=2
				if(score== 3):
					st= (dtVal, dtVal, percDiff)
					#print st
					cnt=cnt+1
					outputList.append(st)
			dtVal = dtVal + timedelta(days=1)
    #print cnt
    # print "N & P ::::::"+ str(N)+":::::::::"+str(P)
    return outputList