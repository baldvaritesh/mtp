'''
Author: Kapil Thakkar
Reference: 
Cheng, H., Tan, P.N., Potter, C. and Klooster, S.A., 2009, January. Detection and Characterization of Anomalies in Multivariate Time Series. In SDM (Vol. 9, pp. 413-424).

'''


import numpy
from math import exp
from numpy import linalg as LA
from numpy import matrix
from numpy import linalg
# Similarity Measure using RBF Function
'''
This function takes 2 arguments:
X : Array of arrays
sigma : Tunable parameter, by default 1

Explanation:

As this function is used to calculate similarity measure among multiple timeseries, X is list of lists.
Where each list inside X, represents 1 series.

sigma is parameter used in rbf function:

    K(i,j) = exp(- (Sum of (k=1 to p))(x.ki - x.kj)^2 / sigma^2)
    
Where p is number of series

Returns 2D Metrix, where each cell (i,j) is similarity measure calculated using above formula.

Requirements : Length of each series should be same
'''
def rbfSimilarity(X, sigma=1):
    numOfSeries = len(X)
    # Length of each series
    n = len(X[0])
    
    # Generates 2D array of size n*n, each element is set to zero
    K = numpy.empty((n,n))
    K.fill(0)
    
    for i in range(0,n):
        for j in range(0,n):
            temp = 0
            for p in range(0,numOfSeries):
                temp += (X[p][i] -X[p][j])*(X[p][i] -X[p][j])
            temp = 0-temp
            temp = temp / (sigma * sigma)
            K[i][j] = exp(temp)
            
    return K

'''
This function takes 2D square matrix as input and returns its (eigenvalues,eigenvectors)
'''
def eigenVectors(K):
    # Returns eigenvalues and right eigenvectors of a square array.
    eigenvalues,eigenvectors = LA.eig(K)
    return (eigenvalues,eigenvectors)

'''
This is helper function used in weights() function to calculate complex numerator
'''
def numeratorForWeights(v,Ky):
    # Length of eigenvectors
    n = len(v)
    v = numpy.array(v)[numpy.newaxis]
    vt = v.transpose()
    # Convert both of them to matrix
    v= numpy.matrix(v)
    vt= numpy.matrix(vt)
    # TODO: CHECK
    # vvt = v * vt
    vvt = vt * v
    vvt = numpy.array(vvt)
    frobeniusInnerProduct = 0
    for i in range(0,n):
        for j in range(0,n):
            frobeniusInnerProduct += (vvt[i][j] * Ky[i][j])            
    return frobeniusInnerProduct
        
'''
Given eigenvalues, eigenvectors and Ky, calculates weight parameters alpha-i
'''
def weights(eigenvalues, eigenvectors, Ky, mu = 1):
    # Number of weights
    n = len(eigenvalues)
    # Initialising array
    alpha = numpy.empty(n)
    alpha.fill(0)
    # Calculating each element
    for i in range(0,n):
        alpha[i] = eigenvalues[i] + (numeratorForWeights(eigenvectors[i],Ky)) / (2*mu)
    return alpha

'''
This function takes weights and eigenvectors as input and retuns aligned kernel matrix Ka
'''
def alignedKernelMatrix(alpha, eigenvectors):
    # Get how many rows
    n = len(eigenvectors)
    Ka = numpy.empty((n,n))
    Ka.fill(0)
    
    for i in range(0,n):
        # TODO: CHECK
        Ka += (alpha[i] * eigenvectors * eigenvectors.transpose())
    return Ka

'''
This function shifts elemenst of matrices so that it does not have any negative value in it.
'''
def shiftToRemoveNegativeVals(Ka):
    minElement = Ka.min()
    return (Ka + abs(minElement))

'''
Aligns two kernels Kx and Ky and returns Ka, aligned matrix.
Where Kx is predictor variable and Ky is target variable.
Kx and Ky are kernel matrices, obtained by applying similarity function.
'''

def kernelAlignment(Kx,Ky):
    # Get eigenvalues and eigenvectors of Kx
    (eigenvalues,eigenvectors) = eigenVectors(Kx)
    # Get weights
    alpha = weights(eigenvalues, eigenvectors, Ky)
    # Get aligned kernel matrix
    Ka = alignedKernelMatrix(alpha, eigenvectors)
    Ka = shiftToRemoveNegativeVals(Ka)
    return Ka

'''
This function normalises matrix K and returns normalised Kernel matrix
'''
def normalise(K):
    n = len(K)
    # Get sum of all columns for normalising
    sumOfCols = numpy.empty(n)
    sumOfCols.fill(0)    
    for j in range(0,n):
        for i in range(0,n):
            sumOfCols[j] += K[i][j]    
    for i in range(0,n):
        for j in range(0,n):
            K[i][j] = K[i][j] / sumOfCols[j]
    return K

'''
Prforms random walk on matrix M
Returns Connectivity Vector c
'''
def randomWalk(S, damping_factor = 0.5, max_iterations = 25, epsilon = 0.0001):
    # Get number of points
    n = len(S)
    # Initialise Connectivity Vector c
    c_old = numpy.empty(n)
    c_old.fill(0)
    c_old = numpy.array(c_old)[numpy.newaxis]
    c_old = c_old.transpose()
    # Preparing damping_vector
    damping_vector = numpy.empty(n)
    damping_vector.fill(float(damping_factor) / float(n))
    damping_vector = numpy.array(damping_vector)[numpy.newaxis]
    damping_vector = damping_vector.transpose()
    
    S = numpy.matrix(S)
    c_old = numpy.matrix(c_old)
    damping_vector = numpy.matrix(damping_vector)
    
    c = 0
    for i in range(0,max_iterations):
        c = damping_vector + (1-damping_factor) * S.transpose() * c_old
        delta = numpy.linalg.norm(c-c_old)
        # TODO: CHECK
        if (delta < epsilon):
            break
        c_old = c
    return c

'''
Anomaly Detection by Random Walk on Graph
Takes Two arguments,
Predictor Variable : List of list
Target Variable: Single List but as a list inside list too
Returns result of random Walk
'''

def graphBasedAnomaly(PredictorVariable, TargetVariable):
    # Get Kernel Matrices for both 
    Kx = rbfSimilarity(PredictorVariable)
    Ky = rbfSimilarity(TargetVariable)
    # Align Them
    Ka = kernelAlignment(Kx,Ky)
    # Normalise Them
    S = normalise(Ka)
    # Apply Random Walk on normalised matrix
    result = randomWalk(S)
    return result

'''
Anomaly Detection by Random Walk on Graph
Takes Three arguments,
Predictor Variable : multiple lists which are predictor variable as multiple args in the format of (date, vals)
Target Variable: Single List of format (date, vals)
threshold : if connectivity by random walk is below threshold value then return it
Returns result of random Walk
'''
def graphBased( threshold, TargetVariable,*PredictorVariable):
    # Fetching values of target variable
    target_vals = [row[1] for row in TargetVariable ]
    target_vals = [target_vals]
    # Fetching vals for predictor
    predict_vals = []
    for li in PredictorVariable:
        temp = [row[1] for row in li]
        predict_vals.append(temp)
    randomWalkResults = graphBasedAnomaly(predict_vals,target_vals)
    result = []
    for i in range(0,len(randomWalkResults)):
        if(randomWalkResults[i] < threshold):
            result.append(TargetVariable[i][0],randomWalkResults[i])
    return result
        
    

'''
Testing

'''

print graphBasedAnomaly(0.2, [[3,2582,3],[1,2,9],[10000,5,3]],[[10,200,3]])