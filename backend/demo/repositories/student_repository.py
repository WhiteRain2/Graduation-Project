# demo/repositories/student_repository.py
from django.core.exceptions import ValidationError
from demo.models import Student, Course, Community, WishCourse, CompletedCourse
from django.db import transaction
from demo.repositories.community_repository import CommunityRepository


class StudentRepository:
    @staticmethod
    def create_student(student_id, name):
        """
        创建新的学生记录。
        :param student_id: 学生的唯一标识符
        :param name: 学生的姓名
        """
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError(f"Student with id {student_id} already exists.")

        # 创建 Student 实例并保存到数据库
        student = Student(student_id=student_id, name=name)
        student.save()
        return student

    @staticmethod
    def get_student_by_id(student_id):
        """
        根据 ID 获取学生记录。
        """
        return Student.objects.get(pk=student_id)

    @staticmethod
    def get_student_by_name(name):
        """
        根据用户名获取记录
        :param name:
        :return:
        """
        return Student.objects.get(name=name)

    @staticmethod
    def join_community(student_id, community_id):
        """
        学生加入共同体的方法。
        :param student_id: 学生的唯一标识符
        :param community_id: 共同体的唯一标识符
        """
        with transaction.atomic():
            student = StudentRepository.get_student_by_id(student_id)
            # 检查学生当前加入的共同体是否已达到上限
            if student.communities.count() >= student.MAX_COMMUNITIES:
                raise ValidationError(f"Student with id {student_id} has reached the maximum community limit.")
            # 判断共同体是否存在
            try:
                community = CommunityRepository.get_community_by_id(community_id)
            except Community.DoesNotExist:
                raise ValidationError(f"Community with id {community_id} does not exist.")
            if student in community.members.all():
                raise ValidationError(f"Student with id {student_id} has already joined the community.")
            # 调用 CommunityRepository 的方法将学生添加到共同体
            CommunityRepository.add_member_to_community(community_id, student_id)

    @staticmethod
    def leave_community(student_id, community_id):
        community = CommunityRepository.get_community_by_id(community_id)
        student = Student.objects.get(pk=student_id)

        if student not in community.members.all():
            raise ValidationError(f"Student with id {student_id} does not have members.")

        CommunityRepository.remove_member_from_community(community_id, student_id)


    @staticmethod
    def add_wish_course(student_id, course_id):
        """
        为学生添加愿望课程，并且更新相关的共同体愿望课程列表。
        """
        with transaction.atomic():
            student = StudentRepository.get_student_by_id(student_id)

            # 确认愿望课程不是学生已完成的课程
            if student.completed_courses.filter(pk=course_id).exists():
                raise ValueError("Course Completed")
            if student.wish_courses.filter(pk=course_id).exists():
                return
            # 添加愿望课程到学生
            if student.wish_courses.count() >= Student.MAX_WISH_COURSES:
                oldest_wish_course = student.wish_courses.order_by('timestamp').first()
                oldest_wish_course.delete()

            WishCourse.objects.create(student=student, course_id=course_id)

            # 检查并更新共同体的愿望课程列表
            for community in student.communities.all():
                community.update_courses()
