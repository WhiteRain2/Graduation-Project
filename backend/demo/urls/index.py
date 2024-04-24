from django.urls import path
from demo.views.index import getinfo, recommend_communities, operation

urlpatterns = [
    path('getinfo/', getinfo, name='getinfo'),
    path('getrecommend/', recommend_communities, name='recommend_communities'),
    path('operation/', operation, name='operation')
]
