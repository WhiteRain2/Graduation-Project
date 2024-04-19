# models/community.py
from django.db import models


class Community(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    completed_courses = models.ManyToManyField(
        'Course',  # 使用字符串代替直接导入
        through='CommunityCompletedCourse',  # 使用字符串代替直接导入
        related_name='communities_completed'
    )
    wish_courses = models.ManyToManyField(
        'Course',  # 使用字符串代替直接导入
        through='CommunityWishCourse',  # 使用字符串代替直接导入
        related_name='communities_wishing'
    )

    MAX_MEMBERS = 8

    def __str__(self):
        return f"Community {self.name}"
