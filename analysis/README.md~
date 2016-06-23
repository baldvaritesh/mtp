# Result Analysis

* Detailed analysis about results and each method is present here:
	- mtp/analysis/resultDoc/results.pdf
	
* Some of Graphs of over all system results for all 4 types of analysis, local and national anomaly analysis can be found in folder:
	- mtp/analysis/moreGraphs/

* Comparison of 2 centre results with default threshold values, 5 center results and 2 center results with user defined threshold values can be found here:
	- mtp/analysis/comparisonOfMultipleResultsPlot/comparisonOfMultipleResults.pdf

* Mumbai,Delhi_Default_Threshold.csv

	These are the primary results on which analysis was performed. In this Linear Regression, Multivariate and slope based methods were run based on the default threshold value. Correlation function was modified to report only those values which had correlation values with opposite signs. For Graph based anomaly, for retail vs average retail and retail vs wholesale 300 anomalies were chosen and for rest 500.
	* For Centre Mumbai
		1. Retail vs Average Retail
			Linear Regression Default Threshold Value: 11.0685657618 (Upto 16, 21, 27)
			Slope Based Default Threshold Value: 1.83510540537, (Upto 45 , 22, over all more till 12) (VAR upto 300)

		2. Retail vs Arrival:
			Linear Regression Default Threshold Value: 59.6237453101 (215, max 281)
			Slope Based Default Threshold Value: -1.05738497599 (-10, max -30) (VAR upto 300)

		3. Retail vs Wholesale:
			Linear Regression Default Threshold Value: 28.1219306191 (max 120)
			Slope Based Default Threshold Value: 1.70285140552 (max 43, usual upto 10) (VAR max 300+)

		4. Wholesale vs Arrival:
			Linear Regression Default Threshold Value: 75.2478685052 (207, 346 and 98 , 3 values only)
			Slope Based Default Threshold Value: -1.2284247661 (max -65, overall -14) (VAR 374 max)

	* For Centre Delhi
		1. Retail vs Average Retail
			Linear Regression Default Threshold Value: 7.19726385328 (max 32)
			Slope Based Default Threshold Value: 1.67347476154 (max upto 12, rest 110,23,80) (VAR max 304)

		2. Retail vs Arrival:
			Linear Regression Default Threshold Value: 73.5330344537 (231, 219, 79 to 87) 
			Slope Based Default Threshold Value: -1.00143073648 (-7 maximum upto, -19 max) (VAR max 301)

		3. Retail vs Wholesale:
			Linear Regression Default Threshold Value: 13.4930780639 (max 30)
			Slope Based Default Threshold Value: 1.38492016881 (maximum in 13,22,25,26) (VAR max 303)

		4. Wholesale vs Arrival:
			Linear Regression Default Threshold Value: 69.1731592917 (81, 233, 300, 96, 72-78, these 4-5 values only)
			Slope Based Default Threshold Value: -0.914313966621 (-8, max -11) (VAR max 450)
			
* fiveCentresResult.csv
	This file contains results when system was run on data of 5 centres:
		- Mumbai
		- Delhi
		- Ahmedabad
		- Bengalore
		- Patna
		
* MumbaiDelhi_userThresholdResult.csv
	This file contains results when we used user defined threshold for 2 centres, Mumbai and Delhi. Thresholds used can be found in code file:
		- mtp/library/fullAnalysis.R
		
* localNation2Center.csv
	This file contains results when we seggregated local and national anomalies for 2 cenres Mumbai and Delhi. We took out common anomalies and stated as national and rest are stated as local to that center.
	
