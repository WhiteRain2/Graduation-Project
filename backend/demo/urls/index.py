from django.urls import path
from demo.views.index import recommend_communities, operation, regis
from demo.views.getInformation.index import GetInfoView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('getinfo/', GetInfoView.as_view(), name='getinfo'),
    path('getrecommend/', recommend_communities, name='recommend_communities'),
    path('operation/', operation, name='operation'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', regis, name='regis'),
]
