# demo/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/community/(?P<community_id>\w+)_(?P<student_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]