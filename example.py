import metafit

app = metafit.Approximator()

#Optional: Graph data set + fitted curve
app.params.output_plot_file = "standardnormal_fit.png"

#Load data set from a file
for line in open("standardnormal.csv","r").readlines():
	if not "," in line:
		continue
	x,y=line.split(",")
	app.addDataPoint([float(x)],float(y))

app.init()
app.fit()
