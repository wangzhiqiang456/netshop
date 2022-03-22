import jsonpickle as jsonpickle
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from cart.cartmanager import getCartManger,CartItem
from goods.models import Inventory
from order.models import Order, OrderItem
from userapp.models import Address
from utils.alipay import *
from django.db.models import F



class ToOrderView(View):
    def get(self,request):

        #获取请求参数
        cartitems = request.GET.get('cartitems','')

        #判断用户是否登录
        if not request.session.get('user'):
            return render(request,'login.html',{'cartitems':cartitems,'redirect':'order'})
        return HttpResponseRedirect('/order/order.html?cartitems='+cartitems)


class OrderListView(View):
    def get(self,request):
        #获取请求参数
        cartitems = request.GET.get('cartitems','')
        print(cartitems)
        # 将json格式字符串转换成python对象（字典{goodsid:1,colorid:1,sizeid:1}）列表
        # [ {goodsid:1,colorid:1,sizeid:1},{goodsid:1,colorid:1,sizeid:1}]
        cartitemList = jsonpickle.loads("[" + cartitems + "]")

        # 将python对象列表转换成CartItem对象列表
        cartitemObjList = [getCartManger(request).get_cartitems(**item) for item in cartitemList if item]

        # 获取用户的默认收货地址
        address = request.session.get('user').address_set.get(isdefault=True)

        # 获取支付总金额
        totalPrice = 0
        for cm in cartitemObjList:  # 遍历到的cm代表的就是购物车里面的商品的那一行
            totalPrice += cm.getTotalPrice()

        return render(request, 'order.html',
                      {'cartitemObjList': cartitemObjList, 'address': address, 'totalPrice': totalPrice})


#创建AliPay对象
alipay = AliPay(appid='2021000118629540', app_notify_url='http://127.0.0.1:8000/order/checkPay/', app_private_key_path='order/keys/my_private_key.txt',
                 alipay_public_key_path='order/keys/alipay_public_key.txt', return_url='http://127.0.0.1:8000/order/checkPay/', debug=True)

#去支付
class ToPayView(View):
    def get(self,request):

        #1.插入Order表中数据
        #获取请求参数
        import uuid,datetime
        data = {
            'out_trade_num':uuid.uuid4().hex,
            'order_num':datetime.datetime.today().strftime('%Y%m%d%H%M%S'),
            'payway':request.GET.get('payway'),    #支付方式
            'address':Address.objects.get(id=request.GET.get('address','')),
            'user':request.session.get('user','')
        }

        print(data)

        orderObj = Order.objects.create(**data)  #创建数据库表，**data指的是要插入的数据，也可以一个一个的写入


        #2.插入OrderItem表中数据
        print(request.GET.get('cartitems','')),'=========================='

        cartitems = jsonpickle.loads(request.GET.get('cartitems'))

        print(cartitems)

        orderItemList = [OrderItem.objects.create(order=orderObj,**item) for item in cartitems if item]

        totalPrice = request.GET.get('totalPrice')[1:]  #￥这个不要即从1开始

        #3.获取扫码支付的页面
        params = alipay.direct_pay(subject='京东超市', out_trade_no=orderObj.out_trade_num, total_amount=str(totalPrice))

        #拼接请求地址
        url = alipay.gateway+'?'+params

        return HttpResponseRedirect(url)

#检查支付状态
class CheckPayView(View):
    def get(self,request):
        #校验是否支付成功（验签的过程）获取所有的请求参数
        params = request.GET.dict()
        #获取签名
        sign = params.pop('sign')

        if alipay.verify(params,sign):
            # 修改订单表中的支付状态
            out_trade_no = params.get('out_trade_no', '')
            order = Order.objects.get(out_trade_num=out_trade_no)
            order.status = u'待发货'    #支付成功后将待支付修改为待发货
            order.save()

            # 修改库存
            orderitemList = order.orderitem_set.all()
            [Inventory.objects.filter(goods_id=item.goodsid, size_id=item.sizeid, color_id=item.colorid).update(
                count=F('count') - item.count) for item in orderitemList if item]     #Inventory指库存

            # 修改购物表
            [CartItem.objects.filter(goodsid=item.goodsid, sizeid=item.sizeid, colorid=item.colorid).delete() for item
             in orderitemList if item]

            return HttpResponse('支付成功！')

        return HttpResponse('支付失败！')
