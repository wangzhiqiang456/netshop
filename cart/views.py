from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views import View

from cart.cartmanager import getCartManger


class AddCartView(View):
    def post(self,request):
        # 在多级字典数据的时候，需要手动设置modified=True,时时的将数据存放到session对象中
        request.session.modified = True
        # 1.获取当前操作类型
        flag = request.POST.get('flag', '')

        # 2.判断当前操作类型
        if flag == 'add':      #将商品加入到购物车
            # 创建cartManager对象
            carManagerObj = getCartManger(request)
            # 加入购物车操作
            carManagerObj.add(**request.POST.dict())

        elif flag == 'plus':   #加入到购物车后，增加商品的数量
            # 创建cartManager对象
            carManagerObj = getCartManger(request)
            # 修改商品的数量（添加）(更新数据库)
            carManagerObj.update(step=1, **request.POST.dict())

        elif flag == 'minus':   #加入到购物车后，减少商品的数量
            # 创建cartManager对象
            carManagerObj = getCartManger(request)
            # 修改商品的数量(减少)(更新数据库)
            carManagerObj.update(step=-1, **request.POST.dict())

        elif flag == 'delete':    #实现移除商品功能
            # 创建cartManager对象
            carManagerObj = getCartManger(request)
            # 逻辑删除购物车选项(即实现移除商品的功能)
            carManagerObj.delete(**request.POST.dict())

        return HttpResponseRedirect('/cart/queryAll/')

class CartListView(View):
    def get(self,request):
        # 创建cartManager对象
        carManagerObj = getCartManger(request)

        #查询所有购物项信息
        cartList = carManagerObj.queryAll()


        return render(request,'cart.html',{'cartList':cartList})
