import osciCard.controller as card
import matplotlib.pyplot as plt 
import numpy as np
import math

fig = plt.figure()        
ax = fig.add_subplot(111)
ax.set_ylabel("Voltage [V]")
ax.set_xlabel("Time [s]")
fig.canvas.set_window_title("x^2")
t=[1,4,9,16,25]
a = []
print a
for x in range(1,5): 
    print x
    y = [x*ti for ti in zip(t)]
    ax.plot(t,y)
    x += 1
    a.append(y)
    print a
plt.show()
