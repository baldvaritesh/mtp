import subprocess
from datetime import datetime
from Utility import csvTransform

command = 'Rscript'
path2script = '/home/kapil/Desktop/mtp/library/graphBasedAnomaly.R'

# Variable number of args in a list

args = ['1','3474','/home/kapil/Desktop/mtp/library/csvGB/AhmedabadRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/BengaluruRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/MumbaiRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/PatnaRetail.csv','/home/kapil/Desktop/mtp/library/csvGB/DelhiRetail.csv']

# Build subprocess command
cmd = [command, path2script] + args

# check_output will run the command and store to result
x = subprocess.check_output(cmd, universal_newlines=True)

print x

# dt= datetime.strptime('2010-01-01' , '%Y-%m-%d')
# csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/Retailresults.csv",dt)