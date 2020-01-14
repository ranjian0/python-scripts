import functools

def NUM_REP(n, base=1000, strings="KMBT", precision=2):
    P = len(strings)
    while n < base**P: P-=1
    return f"{n / base**P:.{precision}f}{('' if P < 0 else strings[P])}"

F_BYTES = functools.partial(NUM_REP, base=1024, strings='KMGTPZY')
F_WEIGHT_METRIC = functools.partial(NUM_REP, base=1000, strings=['g', 'Kg', 'T'])
F_THOUSANDS = functools.partial(NUM_REP)

print(F_WEIGHT_METRIC(1000_000))

