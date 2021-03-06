# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

#import plotly.plotly as py
#import plotly.graph_objs as go

# MatPlotlib
import matplotlib.pyplot as plt
from matplotlib import pylab

from pylab import *
from scipy import stats


# Scientific libraries
import numpy as np

points = np.array([(1, 1), (2, 4), (3, 1), (9, 3)])

# get x and y vectors
x = points[:,0]
y = points[:,1]

# calculate polynomial
z = np.polyfit(x, y, 3)
f = np.poly1d(z)
print f

# calculate new x's and y's
x_new = np.linspace(x[0], x[-1], 50)
y_new = f(x_new)

fig, ax = plt.subplots()

plt.plot(x,y,'o', x_new, y_new)
pylab.title('Polynomial Fit with Matplotlib')
ax = plt.gca()
ax.set_axis_bgcolor((0.898, 0.898, 0.898))
#fig = plt.gcf()
#py.plot_mpl(fig, filename='polynomial-Fit-with-matplotlib')
savefig('polyfit')
plt.show()
