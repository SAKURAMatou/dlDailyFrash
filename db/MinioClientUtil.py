from minio import Minio
from django.core.files.storage import Storage
import time


class MinioClient(object):
    '''
    操作minio文件系统的工具类
    '''
    bucket = "dltest"  # 标明文件存储的桶
    dateStr = time.strftime("%Y/%m/%d", time.localtime())  # 文件存储文件路径是年/月/日/文件名
    fileName = ""  # 文件名称
    # 文件访问路径是bucket/dateStr/文件名
    furl = ""

    def __init__(self):
        self.client = Minio(
            "192.168.233.5:9000",
            access_key="minio01",
            secret_key="minio0111111",
            secure=False
        )

    def upLoadFile(self, name, content):
        self.fileName = name
        # TODO minio文件上传
        bucket = "dltest"
        putName = f"{self.dateStr}/{self.fileName}"
        found = self.client.bucket_exists("dltest")
        if not found:
            # 桶不存在时创建桶
            self.client.make_bucket(bucket)
        self.client.put_object(bucket, putName, content, content.size)
        self.furl = f"/{self.bucket}/{self.dateStr}/{self.fileName}"
        return self.furl


class DjangoToMinio(Storage):
    '''
    继承的django的文件处理类，实现自定义文件存储
    '''

    def __init__(self, base_url):
        if base_url is None:
            self.base_url = base_url = "http://192.168.233.5:9000"
        else:
            self.base_url = base_url

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        '''
        文件上传方法
        name:上传的文件名称
        content:包含上传到文件内容的对象
        '''
        pass
