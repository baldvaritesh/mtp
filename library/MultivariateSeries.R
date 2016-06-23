require(forecast)
require(vars)

MultivariateAnomaly <- function(fileName,hd= FALSE, paramCount,fileStart) {
var.data= read.csv(file = fileName,header=hd)
head(var.data)

objTimeSeries <- list()
for (i in 1:paramCount) {
objTimeSeries[[i]] <- ts(var.data[i])
}

percModelPoints <- 0.60

noOfModelPoints <- trunc(percModelPoints*length(objTimeSeries[[1]]))
noOfRemPoints <- length(objTimeSeries[[1]])- noOfModelPoints
noOfPredictions <- noOfRemPoints

if(noOfRemPoints< noOfPredictions)
{
noOfPredictions <- noOfRemPoints
}

objSampleTimeSeries <- list()
for (i in 1:paramCount) {
objSampleTimeSeries[[i]] <- window(objTimeSeries[[i]],start=1,end=noOfModelPoints)
if(i==1){
sampleObjTimeseries <- objSampleTimeSeries[[i]]
}
else{
sampleObjTimeseries <- cbind(sampleObjTimeseries,objSampleTimeSeries[[i]])
}
}

plot(sampleObjTimeseries)

minStDiff <- length(objSampleTimeSeries[[1]])
objStationaryTimeSeries <- list()
for (i in 1:paramCount) {
stDiff <- ndiffs(objSampleTimeSeries[[i]], alpha = 0.05, test = c("adf"))
if(stDiff>0 & stDiff <= length(objSampleTimeSeries[[i]])){
objStationaryTimeSeries[[i]] <- diff(objSampleTimeSeries[[i]],stDiff)
}
else{
objStationaryTimeSeries[[i]] <- objSampleTimeSeries[[i]]
}
if(minStDiff > length(objStationaryTimeSeries[[i]])){
minStDiff <- length(objStationaryTimeSeries[[i]])
}
}

for (i in 1:paramCount) {
objStationaryTimeSeries[[i]] <- window(objSampleTimeSeries[[i]],1,minStDiff)
if(i==1){
allObjTimeseries <- objStationaryTimeSeries[[i]]
}
else{
allObjTimeseries <- cbind(allObjTimeseries,objStationaryTimeSeries[[i]])
}
}

LagFactors <- VARselect(allObjTimeseries, lag.max=60)$selection

var = VAR(sampleObjTimeseries, p=LagFactors[1])

p <- predict(var, n.ahead=noOfPredictions, ci=0.95)


for(i in 1:length(p$fcst))
{
strName <- paste("/home/kapil/Desktop/mtp/library/testingCSV/",fileStart,i,".csv",sep="")
print(strName)
objForecast <- as.data.frame(p$fcst[i])
objForecast[5] <- window(objTimeSeries[[i]],start = noOfModelPoints, end = noOfModelPoints+noOfPredictions-1)
write.csv(objForecast,strName,row.names=TRUE)
}


}

myArgs <- commandArgs(trailingOnly = TRUE)
myArgs[2]
if(myArgs[2]=='TRUE'){
	x <- MultivariateAnomaly(myArgs[1],TRUE,as.integer(myArgs[3]),myAgrs[4])
} else {
	x <- MultivariateAnomaly(myArgs[1],FALSE,as.integer(myArgs[3]),myArgs[4])
}
