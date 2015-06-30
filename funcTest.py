import numpy as np

def addThis(a, b):
	c = a+b
	return c

a=3
b=4
c=addThis(a, b)

print("a + b = c")
print("%d + %d = %d" % (a, b, c))
