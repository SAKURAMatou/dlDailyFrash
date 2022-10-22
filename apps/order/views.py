from django.shortcuts import render
from django.db import transaction


# Create your views here.
@transaction.atomic
def terst():

    savePoint=transaction.savepoint()
    try:
        '''逻辑代码'''
    except Exception as e :
        '''异常时回滚到指定点'''
        transaction.savepoint_rollback(savePoint)
    finally:
        transaction.savepoint_commit(savePoint)
    return ''
