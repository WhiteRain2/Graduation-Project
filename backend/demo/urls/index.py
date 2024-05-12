from django.urls import path
from demo.views.index import recommend_communities, operation, regis
from demo.views.getInformation.get_student_or_community import GetInfoView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from demo.views.getInformation.get_course import get_course_info, search_courses

urlpatterns = [
    path('getinfo/', GetInfoView.as_view(), name='getinfo'),
    path('courses/', get_course_info, name='get_course_info'),
    path('search-courses/', search_courses, name='search_courses'),
    path('getrecommend/', recommend_communities, name='recommend_communities'),
    path('operation/', operation, name='operation'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', regis, name='regis'),
]
