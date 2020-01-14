import math
import operator
from array import array
from functools import wraps

# Math operations for generic Iterables
x = [1, 1]
y = (1, 2)

def assert_param_types(func):
    """ Ensure func's args are of the same type """
    @wraps(func)
    def wrapper(*args, **kwargs):
        types = list(map(type, args))
        if not all([types[i] == types[i+1] for i in range(len(types)-1)]):
            raise TypeError(f"{func.__name__} : Arguments must be of same type, got {dict(zip(types, args))}")
        return func(*args)
    return wrapper
    

def cast(value, _type):
    if _type == array:
        return _type(value.typecode, value)
    return _type(value)
    
@assert_param_types
def add(x, y):
    return cast(map(operator.add, x, y), type(x))

# ~ iadd = lambda x,y: tuple(map(operator.add, x, y))
# ~ imul = lambda x,y: tuple(map(operator.mul, x, y))
# ~ idiv = lambda x,y: tuple(map(operator.truediv, x, y))
# ~ isub = lambda x,y: tuple(map(operator.sub, x, y))
# ~ idot = lambda x,y: sum(tmul( x, y))
# ~ idist = lambda x,y: math.sqrt(tdist_sqr(x,y))
# ~ idist_sqr = lambda x,y: sum(map(operator.pow, tsub( x, y), (2,2)))

print(add(x, y))
