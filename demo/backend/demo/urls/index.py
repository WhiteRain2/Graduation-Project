from django.urls import path, include
from demo.views.index import index

urlpatterns = [
    path('demo/', index, name='index'),
]
