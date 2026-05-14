import os
import sys

def calculate(a, b, c):
    try:
        r = a + b
        print(r)
        if a > 0:
            if b > 0:
                if c > 0:
                    return r * c
                else:
                    return 0
            else:
                return -1
        else:
            return None
    except:
        pass

unused_var = 42
