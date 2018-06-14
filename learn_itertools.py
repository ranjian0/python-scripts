import itertools as it
from pprint import pprint

# =====================================================================================================================================
# itertools.count
# ```````````````
# usage:
# 1.generating range values using islice  or takewhile
vals = list(it.islice(it.count(100, 4), 0, 5))
print("Count with islice \t\t :: ", vals)
#    OR
vals = list(it.takewhile(lambda c : c < 10, it.count(0))) 
print("Count with takewhile \t\t :: ", vals)
#
# 3. Implement duplicate remover, eg to cheek if a file is seen
import collections
seen = collections.defaultdict(it.count)
files = ["one.txt", "two.txt", "three.txt", "two.txt"]
files = [
	fn
	for fn in files
	if not next(seen[fn])
]
print("NO DUPLICATES \t\t\t::", files)
# 4. Better enumerate
#    if you want to enumerate with support for jump or floats
print("Better Enumerate")
items = ["ian", "joy", "leon"]
for idx, item in zip(it.count(1, 2), items):
	print(idx, " --> ", item)

# =====================================================================================================================================
# itertools.cycle
# ```````````````
# usage:
# 1. helper for using zip with list and single value
name = ["Ian"]
properties = ["21 yrs", "Brown Eyes", "Slim"]
attrs = list(zip(it.cycle(name), properties))
pprint(attrs)

# 2. Slide Show
#    slide_show = cycle(images)

# 3. Simple status indicator
import os, time
status = it.cycle(['','.', '..', '...'])
#for _ in range(10):
	#print("Calculating ", next(status))
	#time.sleep(.5)
	#os.system('clear')
	
# 4. Generating set of repeat commands eg for testing
statements_and_params = zip(it.cycle(["INSERT INTO test3rf.test (k, v) VALUES (%s, 0)"]),
                                    [(i, ) for i in range(100)])
# execute(statements_and_params)

# 5. Iterator Algebra
import operator
from fractions import Fraction
inf_frac = it.accumulate(map(operator.truediv, it.cycle([1, -1]), it.count(1, 2)))
vals = [Fraction(f).limit_denominator(1000) for f in it.islice(inf_frac, 0, 10)]
print(vals)

# =====================================================================================================================================
# itertools.repeat
# ````````````````
# usage:
# 1. Fast looping a fixed number of times
for _ in it.repeat(None, 1000):
	pass
	
# 2. Provide constant stream of values
powers = list(
	map(pow, range(10), it.repeat(2))
)
print(powers)

# 3. zip with single value
name = "Ian"
properties = ["21 yrs", "Brown Eyes", "Slim"]
attrs = list(zip(it.repeat(name), properties))
pprint(attrs)



