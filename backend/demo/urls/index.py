from django.urls import path
from demo.views.index import getinfo, recommend_communities, operation

urlpatterns = [
    path('getinfo/<int:user_id>/', getinfo, name='getinfo'),  # 定义捕获 userId 的路由
    path('getrecommend/', recommend_communities, name='recommend_communities'),
    path('operation/', operation, name='operation')
]
