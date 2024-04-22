# models/relations.py

from django.db import models


class CommunityCompletedCourse(models.Model):
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return f"Community {self.community.id} completed: {self.course.name}"


class CommunityWishCourse(models.Model):
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Community {self.community.id} wishes: {self.course.name}"


class CompletedCourse(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"Student {self.student.student_id} completed: {self.course.name} with score: {self.score}"


class WishCourse(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Student {self.student.student_id} wishes: {self.course.name}"