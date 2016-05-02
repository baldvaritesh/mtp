<html>
<body>
	<h1>Input CSV Files</h1>
	<form action="/inputCSVs" method="post" enctype="multipart/form-data">
	<table>
	%for i in range(csvCount):
		<tr><td>Input CSV#{{i+1}}</td><td><input type ="file" name="CSV{{i+1}}"></td><td><input type="checkbox" name="CSVcheckBox" value="{{i+1}}">Smoothing Needed</td></tr>				
	%end 
	</table>
	<input type="submit" name="submit"> 
	</form>
</body>
</html>
