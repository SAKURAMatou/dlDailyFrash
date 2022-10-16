from haystack import indexes
from apps.goods.models import GoodsSKU


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    '''索引类名是对应的model的类名+index；'''
    # use_template指定创建索引的字段，单独在文件中创建
    text = indexes.CharField(document=True, use_template=True)

    # 必须要有的重载方法，返回model类对象
    def get_model(self):
        return GoodsSKU

    # 建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
