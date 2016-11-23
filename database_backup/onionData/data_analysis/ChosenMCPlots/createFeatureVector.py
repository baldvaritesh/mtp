import chosenmcplots as cp
import whitening as wt
import csv
import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import statsmodels as sm
import scipy, numpy as np

filename = 'anom0.txt'
data = []
with open(filename, 'r') as f:
	reader = csv.reader(f, dialect='excel', delimiter='\t')
	for row in reader:
		data.append(row)

new_centres = wt.c[0]

