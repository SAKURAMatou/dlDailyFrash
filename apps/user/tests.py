import urllib3
from django.test import TestCase
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import TimestampSigner

from minio import Minio

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

client = Minio(
    "192.168.233.5:9000",
    access_key="admin",
    secret_key="admin11111",
    secure=False
)
# 判断数据存储的桶是否存在
found = client.bucket_exists("dltest")
if not found:
    client.make_bucket("dltest")
else:
    print("Bucket 'dltest' already exists")
    response = client.get_object("dltest", "20220116_110735.jpg")
    f = client.fput_object("dltest", "68858462_p0.jpg", r"E:\图片\68858462_p0.jpg")
    # client.
    # print(response.data)
    print(f)
