from django.urls import path, include
from demo.views.index import index
from demo.views.getInformation.index import getinfo
from demo.views.recommend.index import recommend_communities

urlpatterns = [
    path('getinfo/<int:userId>/', getinfo, name='getinfo'),  # 定义捕获 userId 的路由
    path('getrecommend/', recommend_communities, name='recommend_communities'),
]
