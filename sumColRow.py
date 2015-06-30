import numpy as np

a = np.arange(12).reshape(4,3)
b = a.sum(axis=0)
c = a.sum(axis=1)

print(a)
print(b)
print(c)
