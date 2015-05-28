import numpy as np
from matplotlib import pyplot as plt

a = np.random.standard_normal(500)
b = np.random.standard_normal(500)

fig = plt.figure()
plt.plot(a,b,',')
plt.show()

