from itertools import izip

precipitation = r"C:\Users\n47-jones\Desktop\ENGAGE-master\rainfall.txt"

baseflow = r"C:\Users\n47-jones\Desktop\ENGAGE-master\baseflow.txt"

output_baseflow = r"C:\Users\n47-jones\Desktop\ENGAGE-master\baseflow_output.txt"

precipitation_read = open(precipitation)

baseflow_read = open(baseflow)

# Create a textfile to store the output baseflow values
output_baseflow = open(output_baseflow, 'w')

for precipitation, baseflow in izip(precipitation_read, baseflow_read):
    precipitation = precipitation.strip()
    baseflow = baseflow.strip()
    output_baseflow.write(baseflow + " " + precipitation + "\n")
