import subprocess
from datetime import datetime
from Utility import getColumnFromListOfTuples, removeQuotes


'''
This function takes 3 arguments:
dependentVar: Index of the dependent variable, where dependentVar = function of independantVars
numberOfVals: Each CSV contains how many values?
timeSeriesFileNames: name of the files to which series is stored. File should contain only series values.

Executes R script. Result of R script is stored in file, "GraphBasedAnomalyOp.csv"


'''

def graphBasedAnomalyCall(dependentVar, numberOfVals, timeSeriesFileNames):
    command = 'Rscript'
    path2script = '/home/kapil/Desktop/mtp/library/graphBasedAnomaly.R'
    
    # Variable number of args in a list
    
    # Now instead of var args we need CSVs
    
    # args = [str(dependentVar),str(numberOfVals),'/home/kapil/Desktop/mtp/library/csvGB/AhmedabadRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/BengaluruRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/MumbaiRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/PatnaRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/DelhiRetail.csv']
    
    args = [str(dependentVar),str(numberOfVals)]
    for i in range(0,len(timeSeriesFileNames)):
        args.append(timeSeriesFileNames[i])
    
    # Build subprocess command
    cmd = [command, path2script] + args
    
    # check_output will run the command and store to result
    x = subprocess.check_output(cmd, universal_newlines=True)
    
    print x
    
    # dt= datetime.strptime('2010-01-01' , '%Y-%m-%d')
    # csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/Retailresults.csv",dt)

'''
Pass list of CSVs, where
lists[i] = list of tuple of the form (date, val)
where date is in form of string

dateIndex: column number of date in list (starting with 0)
seriesIndex: column number of series in list (starting with 0)

returns (dates,fileNames)
fileNames: Generates multiple CSVs, corresponding to each series for the input of R script. Returns name of these files.
dates: Also separates dates and return it, so that result can be combined with the date
'''
def generateCSVsForGraphBasedAnomaly(lists, dateIndex, seriesIndex):
    dateInString = getColumnFromListOfTuples(lists[dateIndex],0)
    fileNames = []
    for i in range(0,len(lists)):
        # Take out vals from it and print it to csv file
        name = 'input'+ str(i) + 'GBA.csv'
        fileWriter = open(name,'w')
        for Tuple in lists[i]:
            fileWriter.write(str(Tuple[seriesIndex]) + "\n")
        fileWriter.close()
        fileNames.append(name)
    # dates = [ datetime.strptime(date, "%Y-%m-%d") for date in dateInString]
    return (dateInString,fileNames)

'''
This function takes 3 arguments:

dates : List of dates
resultFile: Path of file to which output of graph based anomaly is written
numOfPtsReqd: Number of anomalous points required


reurns list of tuples of the form:
(start_date, end_date, connectivity_value)

'''
def getAnomalies(dates,resultFile, numOfPtsReqd):    
    results = []
    for i,line in enumerate(open(resultFile)):
        if(i==0):
            continue
        line = line.strip()
        tokens = line.split(",")
        
        date = dates[i-1]
        value = float(removeQuotes(tokens[2]))
        rank = int(removeQuotes(tokens[3]))
        results.append((date,value,rank))
    
    # Sort by rank
    results = sorted(results, key=lambda x: x[2])
    
    # Take top numOfPtsReqd
    results = results[0:numOfPtsReqd]
    
    # Sort by date
    results = sorted(results, key=lambda x: x[0])    
    results = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(a, "%Y-%m-%d"),b) for (a,b,c) in results]
    return results

'''
This function takes following arguments:

numOfPtsReqd: Number of anomalous points required
lists: Pass list of CSVs, where, lists[i] = list of tuple of the form (date, val), where date is in form of string and there can be multiple vals
dateIndex: column number of date in list (starting with 0)
seriesIndex: column number of series in list (starting with 0)
dependentVar: Index of the dependent variable in the "lists", where dependentVar = function of independantVars
numOfPtsReqd: Number of anomalous points required
'''
def graphBasedAnomalyMain(lists, dependentVar, numOfPtsReqd, dateIndex=0, seriesIndex=1):
    (dates,fileNames) = generateCSVsForGraphBasedAnomaly(lists, dateIndex, seriesIndex)
    graphBasedAnomalyCall(dependentVar, len(dates), fileNames)
    return getAnomalies(dates, "GraphBasedAnomalyOp.csv", numOfPtsReqd)