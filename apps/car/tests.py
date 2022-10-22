from functools import reduce

from django.test import TestCase

# Create your tests here.

li = ['1', '2', '4', '5', '7', '42']
t = reduce(lambda a, b: int(a) + int(b), li)
print(t)
