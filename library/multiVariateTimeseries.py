import subprocess
from datetime import datetime
from Utility import csvTransform

def multivaraiateAnalysis(args):
    command = 'Rscript'
    path2script = '/home/kapil/Desktop/mtp/library/MultivariateSeriesModified.R'
    
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
