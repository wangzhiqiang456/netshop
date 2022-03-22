import math

from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from django.views import View
from goods.models import *



class IndexView(View):
    def get(self,request,cid=1):

        cid = int(cid)
        num = request.GET.get('num',1)
        n = int(num)

        #查询类别信息
        categorys = Category.objects.all().order_by('id')
        #查询当前类别下的所以商品信息
        goodsList = Goods.objects.filter(category_id=cid).order_by('id')

        #分页，每页显示8条数据
        pager = Paginator(goodsList,8)

        goodsList = pager.page(n)

        # 每页开始页码
        begin = (n - int(math.ceil(10.0 / 2)))
        if begin < 1:
            begin = 1

        # 每页结束页码
        end = begin + 9
        if end > pager.num_pages:
            end = pager.num_pages

        if end <= 10:
            begin = 1
        else:
            begin = end - 9

        pagelist = range(begin, end + 1)

        return render(request,'index.html',{'categorys':categorys,'goodsList':goodsList,'currentCid':cid,'pagelist':pagelist,'currentNum':n})

def recommend_view(func):
    def wrapper(detailView,request,goodsid,*args,**kwargs):
        #将存放在cookie中的goodsId获取
        cookie_str = request.COOKIES.get('recommend','')


        #存放所有goodsid的列表
        goodsIdList = [gid for gid in cookie_str.split() if gid.strip()]

        #思考1：最终需要获取的推荐商品
        goodsObjList = [Goods.objects.get(id=gsid) for gsid in goodsIdList if gsid!=goodsid and Goods.objects.get(id=gsid).category_id==Goods.objects.get(id=goodsid).category_id][:4]

        #将goodsObjList传递给get方法
        response = func(detailView,request,goodsid,goodsObjList,*args,**kwargs)


        #判断goodsid是否存在goodsIdList中
        if goodsid in goodsIdList:
            goodsIdList.remove(goodsid)
            goodsIdList.insert(0,goodsid)
        else:
            goodsIdList.insert(0,goodsid)

        #将goodsIdList中的数据保存到Cookie中
        response.set_cookie('recommend',' '.join(goodsIdList),max_age=3*24*60*60)


        return response

    return wrapper

class DetailView(View):

    @recommend_view

    def get(self,request,goodsid,recommendList=[]):
        goodsid = int(goodsid)
        # 根据goodsid查询商品详情信息(即获得goods对象)
        goods = Goods.objects.get(id=goodsid)

        return render(request,'detail.html',{'goods':goods,'recommendList':recommendList})