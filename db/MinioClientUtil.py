from minio import Minio
import time

'''
操作minio文件系统的工具类
'''


class MinioClient(object):
    bucket = "dltest"  # 标明文件存储的桶
    dateStr = time.strftime("%Y/%m/%d", time.localtime())  # 文件存储文件路径是年/月/日/文件名
    fileName = ""  # 文件名称
    # 文件访问路径是bucket/dateStr/文件名
    furl = f"/{bucket}/{dateStr}/{fileName}"

    def __init__(self):
        self.client = Minio(
            "192.168.233.5:9000",
            access_key="minio01",
            secret_key="minio0111111",
            secure=False
        )

    def upLoadFile(self, file):
        self.fileName = file.name
        # TODO minio文件上传
        return f"/{self.bucket}/{self.dateStr}/{self.fileName}"
