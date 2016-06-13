# metafit
Naive, assumption-less curve fitting by simulated annealing

## Requirements
* matplotlib (for visualization)
* sympy (for printing function expressions)

## Usage
`example.py` shows how to use metafit to load and fit 2D data from a .csv file.

## Example Result
Here is an example for the curve fitted (10 iterations) to the standard normal distribution data set from the repository (`standardnormal.csv`). The fitted curve expression was `0.398961428125197*(0.60638179926863**a)**a`. Note that the data set is simply the theoretical p.d.f. of the standard normal distribution.
![Plot](standardnormal_example_fit.png?raw=true)

