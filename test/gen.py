import matplotlib.pyplot as plt
import numpy as np
x=list()
y=list()
for i in range(10000):
	x.append(i)
	y.append(np.random.rand())
plt.plot(x,y)
plt.savefig('workload.png', dpi = 100)
#1475