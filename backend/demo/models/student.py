# models/student.py
from django.db import models


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    MAX_WISH_COURSES = 5

    completed_courses = models.ManyToManyField(
        'Course',  # 使用字符串代替直接导入
        through='CompletedCourse',  # 使用字符串代替直接导入
        related_name='students_completed'
    )
    wish_courses = models.ManyToManyField(
        'Course',  # 使用字符串代替直接导入
        through='WishCourse',  # 使用字符串代替直接导入
        related_name='students_wishing'
    )
    communities = models.ManyToManyField(
        'Community',  # 使用字符串代替直接导入
        related_name='members'
    )

    def __str__(self):
        return f"Student {self.student_id}"
