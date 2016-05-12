require(forecast)
require(vars)

var.data= read.csv(file.choose(),header=FALSE)
head(var.data)

mumbai.wp = ts(var.data[2], frequency=365, start=c(2006), end=c(2015))
mumbai.rp = ts(var.data[3], frequency=365, start=c(2006), end=c(2015))
mumbai.arrival = ts(var.data[4], frequency=365, start=c(2006), end=c(2015))

WPcData = window(mumbai.wp, start=c(2006), end=c(2010))
RPcData = window(mumbai.rp, start=c(2006), end=c(2010))
ArrivalcData = window(mumbai.arrival, start=c(2006), end=c(2010))
onion.ts = cbind(WPcData, RPcData,ArrivalcData)
plot(onion.ts)

ndiffs(WPcData, alpha = 0.05, test = c("adf"))
ndiffs(RPcData, alpha = 0.05, test = c("adf"))
ndiffs(ArrivalcData, alpha = 0.05, test = c("adf"))

d.WPcData = diff(WPcData)
d.RPcData = diff(RPcData)
d.ArrivalcData = diff(ArrivalcData)

onion2.ts = cbind(d.WPcData, d.RPcData,d.ArrivalcData)
plot(onion2.ts)

VARselect(onion2.ts, lag.max=60)$selection

var = VAR(onion2.ts, p=32)
serial.test(var, lags.pt=60, type="PT.asymptotic")

summary(var, equation="d.WPcData")
predict(var, n.ahead=3000, ci=0.95)

fcst = forecast(var)
plot(fcst)