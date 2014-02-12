from scipy import optimize
import numpy as np

a = 10
b = 3

def foo(xy):
    x, y = xy
    return x*x + y*y + 7.5


i = np.array([2, 1])

print(i)

res = optimize.anneal(foo, i, schedule='boltzmann', maxiter=10000)

print(res)

print(foo(res[0]))