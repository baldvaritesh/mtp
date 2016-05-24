import subprocess
from datetime import datetime
from Utility import csvTransform

command = 'Rscript'
path2script = '/home/kapil/Desktop/mtp/library/MultivariateSeriesModified.R'

# Variable number of args in a list

args = ['/home/kapil/Desktop/mtp/library/testingCSV/MumbaiSILData.csv','FALSE','3','2000']

# Build subprocess command
cmd = [command, path2script] + args

# check_output will run the command and store to result
x = subprocess.check_output(cmd, universal_newlines=True)

dt= datetime.strptime('2010-01-01' , '%Y-%m-%d')
csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/Retailresults.csv",dt)
