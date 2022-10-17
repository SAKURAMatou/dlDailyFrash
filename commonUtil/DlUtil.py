import json
from django.http import JsonResponse


def makeJsonResponse(code: int = 0, msg: str = '操作失败', data: dict = None):
    res = {"code": code, 'msg': msg}
    if data is None:
        res.data = data
    return JsonResponse(res)
