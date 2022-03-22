from django.db import models

# Create your models here.
from goods.models import Goods, Color, Size
from userapp.models import UserInfo


class CartItem(models.Model):
    goodsid = models.PositiveIntegerField()
    colorid = models.PositiveIntegerField()
    sizeid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()    #购买的数量
    isdelete = models.BooleanField(default=False)  #是否逻辑删除，是否会将商品从购物车删除
    user = models.ForeignKey(UserInfo,on_delete=models.CASCADE)

    class Meta:
        unique_together = ['goodsid','colorid','sizeid']   #联合唯一，即三者是一体的


    def getGoods(self):
        return Goods.objects.get(id=self.goodsid)

    def getColor(self):
        return Color.objects.get(id=self.colorid)

    def getSize(self):
        return Size.objects.get(id=self.sizeid)

    def getTotalPrice(self):
        import math
        return math.ceil(float(self.getGoods().price) * int(self.count))



