library(stats)
library(base)
library(randomWalkAnomaly)
library(matrixcalc)
library(multivariateAnomaly)


MultivariateAnomaly <- function(dependentVar,fileNames, numOfRows) {
    
    d <- list()
    
    for (i in 1:length(fileNames)) {
        temp <- scan(fileNames[i])
        d[[i]] <- matrix(c(temp),nrow=1,ncol=numOfRows)
    }
    
    

    # c1 <- scan('/home/kapil/Desktop/mtp/library/csvGB/AhmedabadRetail.csv')
    # c2 <- scan('/home/kapil/Desktop/mtp/library/csvGB/BengaluruRetail.csv')
    # c3 <- scan('/home/kapil/Desktop/mtp/library/csvGB/MumbaiRetail.csv')
    # c4 <- scan('/home/kapil/Desktop/mtp/library/csvGB/PatnaRetail.csv')
    # c5 <- scan('/home/kapil/Desktop/mtp/library/csvGB/DelhiRetail.csv')
    
    # c1 <- matrix(c(c1),nrow=1,ncol=3474)
    # c2 <- matrix(c(c2),nrow=1,ncol=3474)
    # c3 <- matrix(c(c3),nrow=1,ncol=3474)
    # c4 <- matrix(c(c4),nrow=1,ncol=3474)
    # c5 <- matrix(c(c5),nrow=1,ncol=3474)

    if(1 != dependentVar) {aw = d[[1]]
    flag = 1}else{aw = d[[2]]
    flag = 2}
    for(i in 1:length(d)) {
        if(i!= dependentVar & i!= flag) {
            print (i)
            aw <- rbind(aw, d[[i]])
        }
    }
    r <- d[[dependentVar]]
    # aw <- rbind(c2,c3,c4,c5)
    # r <- c1

    RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)
    
    
    objForecast <- as.data.frame(RandomWalkOutput)
    write.csv(objForecast,"GraphBasedAnomalyOp.csv",row.names=TRUE)
    
}


myArgs <- commandArgs(trailingOnly = TRUE)
cat(myArgs[3])
dependentVar <- as.integer(myArgs[1])
numOfRows <- as.integer(myArgs[2])
fileNames <- c()
for(i in 3:length(myArgs)) {
    fileNames <- c(fileNames,myArgs[i])    
}
cat(fileNames)

MultivariateAnomaly(dependentVar,fileNames, numOfRows)