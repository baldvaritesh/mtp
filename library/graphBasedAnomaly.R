library(stats)
library(base)
library(randomWalkAnomaly)
library(matrixcalc)
library(multivariateAnomaly)

c1 <- scan('/home/kapil/Desktop/mtp/library/csvGB/AhmedabadRetail.csv')
c2 <- scan('/home/kapil/Desktop/mtp/library/csvGB/BengaluruRetail.csv')
c3 <- scan('/home/kapil/Desktop/mtp/library/csvGB/MumbaiRetail.csv')
c4 <- scan('/home/kapil/Desktop/mtp/library/csvGB/PatnaRetail.csv')
c5 <- scan('/home/kapil/Desktop/mtp/library/csvGB/DelhiRetail.csv')

c1 <- matrix(c(c1),nrow=1,ncol=3474)
c2 <- matrix(c(c2),nrow=1,ncol=3474)
c3 <- matrix(c(c3),nrow=1,ncol=3474)
c4 <- matrix(c(c4),nrow=1,ncol=3474)
c5 <- matrix(c(c5),nrow=1,ncol=3474)



# For C1
aw <- rbind(c2,c3,c4,c5)
r <- c1

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

if(FALSE) {

# For C2
aw <- rbind(c1,c3,c4,c5)
r <- c2

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)



# For C3
aw <- rbind(c1,c2,c4,c5)
r <- c3

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

# For C4
aw <- rbind(c1,c2,c3,c5)
r <- c4

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

# For C5
aw <- rbind(c1,c2,c3,c4)
r <- c5

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

# FOR RETAIL VS ARRIVAL

a1 <- scan('/home/kapil/Desktop/mtp/library/csvGB/AhmedabadArr.csv')
a2 <- scan('/home/kapil/Desktop/mtp/library/csvGB/BengaluruArr.csv')
a3 <- scan('/home/kapil/Desktop/mtp/library/csvGB/MumbaiArr.csv')
a4 <- scan('/home/kapil/Desktop/mtp/library/csvGB/PatnaArr.csv')
a5 <- scan('/home/kapil/Desktop/mtp/library/csvGB/DelhiArr.csv')

a1 <- matrix(c(c1),nrow=1,ncol=3474)
a2 <- matrix(c(c2),nrow=1,ncol=3474)
a3 <- matrix(c(c3),nrow=1,ncol=3474)
a4 <- matrix(c(c4),nrow=1,ncol=3474)
a5 <- matrix(c(c5),nrow=1,ncol=3474)


# For C1
aw <- rbind(a1)
r <- c1

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

if(FALSE) {

# For C2
aw <- rbind(a2)
r <- c2

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)



# For C3
aw <- rbind(a3)
r <- c3

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

# For C4
aw <- rbind(a4)
r <- c4

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)

# For C5
aw <- rbind(a5)
r <- c5

RandomWalkOutput = multivariateAnomaly(aw,r,0,93.14,5)


}
