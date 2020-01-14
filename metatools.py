import time
import logging
from inspect import signature
from functools import wraps, partial

def timethis(func):
    """
    Decorator that reports execution time.
    :- from Python Cookbook, 3rd Edition, Chapter 9 Metaprogramming
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(func.__name__, ": ", end-start)
        return result
    return wrapper


def typeassert(*ty_args, **ty_kwargs):
    """
    Decorator that type checks function arguments
    :- from Python Cookbook, 3rd Edition, Chapter 9 Metaprogramming
    """
    def decorate(func):
        # if in optimized mode, disable type checking
        if not __debug__:
            return func 

        # map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)

            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(
                                "Argument {}, expected {} but got {}".format(name, bound_types[name], type(value))
                            )
            return func(*args, **kwargs)
        return wrapper
    return decorate

def logged(func=None, *, level=logging.DEBUG, name=None, message=None):
    """
    Decorator that logs functions
    :- from Python Cookbook, 3rd Edition, Chapter 9 Metaprogramming
    """
    if func is None:
        return partial(logged, level=level, name=name, message=message)
        
    logname = name or func.__module__
    log = logging.getLogger(logname)
    logmsg = message or func.__name__
    

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.log(level, logmsg)
        return func(*args, **kwargs)
    return wrapper 
    
    
@logged
def add(x, y):
    return x + y 
    
@logged(level=logging.CRITICAL, name='example')
def spam():
    print("Spam!")
    
add(10, 4)
spam()
