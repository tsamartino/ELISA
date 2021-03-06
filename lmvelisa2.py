import statistics
import os

source = "0633-1.txt"

#Open plate and print name
plate = open(source, 'r')
plate_name = "15-"
for char in source:
	if char == ".":
		break
	else:
		plate_name += char
print ("Plate name:", plate_name)
plate.readline()
plate.readline()
plate.readline()

#Creates dictionary sorted by row
#To access A1 - row_dict['A'][0]
row_dict = {}
i = 0
for line in plate:
	if i < 8:
		list_of_values = line.split('\t')
		row_dict[line[0]] = list_of_values[1:13]
		i += 1
plate.close()

#Creates dictionary sorted by column
#To access A1 - column_dict[1][0]
column_dict = {}
for number in range(1,13):
	column_list = []
	for item in sorted(row_dict):
		column_list.append(row_dict[item][number-1])
		column_dict[number] = row_dict[item][number-1]
	column_dict[number] = [float(i) for i in column_list]	

#Creates dictionary sorted by well number
#To access A1 - well_dict[1]
well_dict = {}
well_number = 1
for item in column_dict:
	for x in range(0,8):
		well_dict[well_number] = float(column_dict[item][x])
		well_number += 1

#Establishes where controls are in the plate
#Creates list for each type of control
control_column = 9
#If no Agdia control is loaded, this value should == 0
agdia_well = 64

negative_list = column_dict[control_column][0:3]
positive_list = column_dict[control_column][3:6]
buffer_list = column_dict[control_column][6:8]
agdia_control = well_dict[agdia_well]
positive_wells = [agdia_well, (((control_column-1)*8)+4), (((control_column-1)*8)+5), (((control_column-1)*8)+6)]

#Calculates mean and standard deviation for each control type
negative_mean = statistics.mean(negative_list)
positive_mean = statistics.mean(positive_list)
buffer_mean = statistics.mean(buffer_list)
negative_stdev = statistics.stdev(negative_list)
positive_stdev = statistics.stdev(positive_list)
buffer_stdev = statistics.stdev(buffer_list)

#Calculates the cut-off value and signal:noise from the control means
cutoff = negative_mean * 3
sig_to_noise = positive_mean/negative_mean

#Print statistics for the plate
print("""
The cut-off was set at %.4f
The signal-to-noise ratio is %.2f
""" % (cutoff, sig_to_noise))

#Determines if a well is negative or positive and prints positive wells with O.D. value
sample_size = 60
count = 0
for item in well_dict:
	if well_dict[item] >= cutoff:
		if item in positive_wells:
			continue
		else:
			count += 1
			print ("Well",item,"is POSITIVE with O.D. value of",well_dict[item])
print ("%s out of %s sub-samples tested positive for LMV" % (count, sample_size))

#Builds list with only relevant sample data and mean of the controls
sample = [['Sub-sample', 'O.D. reading', 'Cut-off']]
for x in range(sample_size):
	sample.append([str(x+1), well_dict[x+1], cutoff])
sample.append(['Agdia control', well_dict[agdia_well], cutoff])
sample.append(['Negative control mean', negative_mean, cutoff])
sample.append(['Positive control mean', positive_mean, cutoff])
sample.append(['Buffer control mean', buffer_mean, cutoff])

#Generates an html report using Google Visualization Combo Chart (bar for OD values, line for cutoff)
report = """
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages: ["corechart"]});
google.setOnLoadCallback(drawVisualization);

function drawVisualization() {
	// Plate data

	var dataTable = new google.visualization.DataTable();
	  dataTable.addColumn({ type: 'string', id: 'Sub-sample'})
	  dataTable.addColumn({ type: 'number', id: 'O.D. reading'})
	  dataTable.addColumn({ type: 'number', id: 'Cut-off'})
	  dataTable.addRows(%s)

	var options = {
	  title : 'ELISA results for plate %s',
	  vAxis: {title: "O.D. reading"},
	  hAxis: {title: "Sub-sample"},
	  seriesType: "bars",
	  series: {1: {type: "line"}}
	};

	var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));
	chart.draw(dataTable, options);
}
    </script>
  </head>
  <body>
    <div id="chart_div" style="width: 900px; height: 500px;"></div>
  </body>
</html>
""" % (sample[1:], plate_name)

output_filename = ".".join([source.split(".")[0], "html"])

with open(output_filename, "w") as handle:
	handle.write(report)

#os.system("open %s" % output_filename)






#fuck around space
import json
sorted_wells = [['Sub-sample', 'O.D. reading', 'Cut-off']]
sorted_wells += [[str(i), well_dict[i], cutoff] for i in sorted(well_dict.keys())]
encoded_wells = json.dumps(sorted_wells)

html_container = """
<!doctype html>
<html>
<head>
  <title>Report</title>
  <script type="text/javascript" src="https://www.google.com/jsapi"></script>
  <script>
    var data = %s;

  	google.load('visualization', '1.0', {'packages':['corechart']});
  	
  	function doneDrawingChart() {
  	  var table = new google.visualization.DataTable();
  	  table.addColumn('string', 'Well', 'Cutoff');
  	  table.addColumn('number', 'OD', 'Cutoff');

  	  table.addRows(data);

      var options = {'title':'Seeds and shit',
                       'width':800,
                       'height':700};

      var chart = new google.visualization.ColumnChart(document.getElementById("chart"));
      chart.draw(table, options);
  	  console.log("Finished drawing chart.", data);
  	};

  	google.setOnLoadCallback(doneDrawingChart);
   </script>
</head>

<body>
	Report results
	<div id="chart"></div>
	<script></script>
</body>
</html>
""" % (sample)








