from django.test import TestCase
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import TimestampSigner

from django.conf import settings

# Create your tests here.

# str = {"key": 1231}
# serializer = URLSafeTimedSerializer("test")
# signer = TimestampSigner("test")
# dumped = serializer.dumps(str)
# print(dumped,type(dumped))
#
# print(f'这是字符串{dumped}')

print('18705171234'[-4])
obj = {"key1": 1, "key2": 2}
print(obj.get("key1"), obj.key1)
