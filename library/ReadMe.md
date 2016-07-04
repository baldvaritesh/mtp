# implementation

Hypothesis Methods:

Hypothesis 1:

	* Slope Based Detection
	* Linear Regression Based Method
	* Correlation based method

Hypothesis 2:

	* Slope Based Detection
	* Linear Regression Based Method
	* Correlation based method

Hypothesis 3:

	* Multiple ARIMA
	* Graph based Anomaly Detection

Hypothesis 4:

	* Methods stated for Hypothesis  1 and 2

This folder contains implementation of all these methods. For more detail about this methods and related file explanation refer:
	- mtp/library_documentation/Anomaly Detection.pdf

Analysis performed using following files:
	
	* fullAnalysis.py: With Correlation window size as 15, slope based window as 7 and with default threshold values
	* fullAnalysisWindowLarge.py: With Correlation window size as 20, slope based window as 10 and with default threshold values
	* fullAnalysisWindowSmall.py: With Correlation window size as 7, slope based window as 4 and with default threshold values
	* fullAnalysisUpdated.py: This file is used to find out local and national anomalies. Configurations are same as of fullAnalysis.py.