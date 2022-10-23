import math
import time
from random import random

from django.test import TestCase

# Create your tests here.

payWay_chioce = ((1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银行卡支付'))
print(payWay_chioce)

tf = time.strftime('%Y%m%d%H%M%S', time.localtime()) + str(math.trunc(random() * 10000))

print(tf)
