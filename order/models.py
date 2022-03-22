from django.db import models

# Create your models here.

from userapp.models import Address, UserInfo


class Order(models.Model):
    out_trade_num = models.UUIDField()     #交易凭证
    order_num = models.CharField(max_length=50)    #订单编号
    trade_no = models.CharField(max_length=120,default='')   #支付后生成的唯一编号
    status = models.CharField(max_length=20,default='待支付')   #支付状态
    payway = models.CharField(max_length=20,default='alipay')   # 支付方式，alipay代表支付宝支付
    address = models.ForeignKey(Address,on_delete=models.CASCADE)   #收获地址
    user = models.ForeignKey(UserInfo,on_delete=models.CASCADE)

class OrderItem(models.Model):   #订单的购物项
    goodsid = models.PositiveIntegerField()
    colorid = models.PositiveIntegerField()
    sizeid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
