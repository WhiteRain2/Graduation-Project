# models/community.py
from django.db import models
from .student import Student
from .course import Course
from .relations import CommunityCompletedCourse, CommunityWishCourse
from .similarity import CourseSimilarity


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

    def evaluate_member_similarity(self, student, current_wish_course_id):
        def calculate_course_similarity(course_a_id, course_b_id):
            """
            根据相似性模型获取两门课程之间的相似度
            :param course_a_id: int, 第一门课程的ID
            :param course_b_id: int, 第二门课程的ID
            :return: float, 两门课程之间的相似度评分
            """
            try:
                if course_a_id == course_b_id:
                    return 1
                course_a_similarity_obj = CourseSimilarity.objects.get(course_id=course_a_id)
                return course_a_similarity_obj.similarity_vector.get(str(course_b_id), 0)
            except CourseSimilarity.DoesNotExist:
                # 如果没有找到课程相似性对象，则返回0
                return 0
        """
        根据学生的当前愿望课程以及已完成课程与共同体完成的课程和愿望课程
        列表相匹配的程度，计算学生与共同体的相似度评分。
        :param student: Student, 学生实例
        :param current_wish_course_id: int, 学生当前的愿望课程ID
        :return: float, 学生与共同体的相似度评分
        """
        # 确保学生的愿望课程ID确实存在于学生的愿望课程列表中
        if not student.wish_courses.filter(course_id=current_wish_course_id).exists():
            return -1

        # 计算学生当前愿望课程与共同体已完成课程的相似度
        wish_course_similarity = sum(
            calculate_course_similarity(current_wish_course_id, community_course.course_id)
            for community_course in self.completed_courses.all()
        ) / max(1, self.completed_courses.count())  # 避免除以零

        # 同样的方法，计算学生已完成课程与共同体愿望课程列表的相似度
        completed_course_similarity = sum(
            calculate_course_similarity(student_course.course_id, wish_course.course_id)
            for student_course in student.completed_courses.all()
            for wish_course in self.wish_courses.all()
        ) / max(1, (student.completed_courses.count() * self.wish_courses.count()))  # 避免除以零

        # 最终相似度评分是两部分匹配度的加权平均
        final_similarity_score = 0.5 * wish_course_similarity + 0.5 * completed_course_similarity
        return final_similarity_score

    def __str__(self):
        return f"Community {self.name}"
