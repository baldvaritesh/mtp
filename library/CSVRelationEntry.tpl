<html>
<body>
	<h1>Input CSV Files Relation</h1>
	<form action="/relationEntry" method="post" enctype="multipart/form-data">
	<table border="4">
	%for i in range(csvCount+1):
		<tr>
		%for j in range(csvCount+1):
			%if i==0 and j==0:
				<td> Relates with</td>
			%elif i==0:
				<td> CSV#{{j}}</td>
			%elif j==0:
				<td> CSV#{{i}}</td>
			%else:
				<td><select name={{str(i)+"_"+str(j)}}><option value="1">Positive</option><option value="-1">Negative</option><option value="0">Random</option><option value="-2" selected="selected">Default</option><option value="2">Locate</option></select></td>
			%end
		%end
		</tr>		
	%end 
	</table>
	<input type="submit" name="submit"> 
	</form>
</body>
</html>
