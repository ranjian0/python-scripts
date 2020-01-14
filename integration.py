from scipy.integrate import quad

# Integrate [y = x^2] from x=0 to x=1
def integrand(x):
    return x**2
    
ans, err = quad(integrand, 0, 1)
print(ans)

# Double Integrals
# Integrate f(x, y) = ysin(x) + xcos(y)
# over [pi <= x <= 2pi | 0 <= y <= pi]
from scipy.integrate import dblquad
import numpy as np

def integrand(y, x):
    #XXX Note:: first argument must be y, then x
    return y * np.sin(x) + x * np.cos(y)
    
ans, err = dblquad(integrand, np.pi, 2*np.pi,
                lambda x: 0,
                lambda x: np.pi)
print(ans)

# Integrate f(x,y,z) = ysin(x) + zcox(x) 
# over [0 <= x <= pi | 0 <= y <= 1 | -1 <= z <= 1]
from scipy.integrate import tplquad

def integrand(z, y, x):
    return y * np.sin(x) + z * np.cos(x)
    
ans, err = tplquad(integrand, 
                    0, np.pi,
                    lambda x:0, lambda x:1,
                    lambda x,y:-1, lambda x,y:1)
print(ans)













