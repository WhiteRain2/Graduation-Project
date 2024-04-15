# demo/repositories/student_repository.py
from django.core.exceptions import ValidationError
from demo.models import Student, Course, Community, WishCourse, CompletedCourse
from django.db import transaction
from demo.repositories.community_repository import CommunityRepository


class StudentRepository:
    @staticmethod
    def create_student(**student_data):
        """
        创建新的学生记录。
        """
        return Student.objects.create(**student_data)

    @staticmethod
    def get_student_by_id(student_id):
        """
        根据 ID 获取学生记录。
        """
        return Student.objects.get(pk=student_id)

    @staticmethod
    def update_student(student_id, **update_data):
        """
        更新特定学生的信息。
        """
        Student.objects.filter(pk=student_id).update(**update_data)

    @staticmethod
    def join_community(student_id, community_id, max_communities):
        """
        学生加入共同体的方法。
        :param student_id: 学生的唯一标识符
        :param community_id: 共同体的唯一标识符
        :param max_communities: 学生允许加入的最大共同体数量
        """
        with transaction.atomic():
            student = StudentRepository.get_student_by_id(student_id)

            # 检查学生当前加入的共同体是否已达到上限
            if student.communities.count() >= max_communities:
                raise ValidationError(f"Student with id {student_id} has reached the maximum community limit.")

            # 判断共同体是否存在
            try:
                community = CommunityRepository.get_community_by_id(community_id)
            except Community.DoesNotExist:
                raise ValidationError(f"Community with id {community_id} does not exist.")

            # 调用 CommunityRepository 的方法将学生添加到共同体
            CommunityRepository.add_member_to_community(community_id, student_id)

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
            if student.wish_courses.count() < Student.MAX_WISH_COURSES:
                new_wish_course = WishCourse.objects.create(student=student, course_id=course_id)
            else:
                oldest_wish_course = student.wish_courses.order_by('timestamp').first()
                oldest_wish_course.delete()
                new_wish_course = WishCourse.objects.create(student=student, course_id=course_id)

            # 检查并更新共同体的愿望课程列表
            for community in student.communities.all():
                wish_courses_count = community.wish_courses.count()
                if wish_courses_count < 3 and not community.completed_courses.filter(pk=course_id).exists():
                    community.wish_courses.add(new_wish_course.course)

    @staticmethod
    def add_completed_course(student_id, course_id):
        """
        为学生添加已完成课程，并且从相关的共同体愿望课程列表中删除此课程。
        """
        with transaction.atomic():
            student = StudentRepository.get_student_by_id(student_id)
            course = Course.objects.get(pk=course_id)

            # 为学生添加已完成课程
            CompletedCourse.objects.create(student=student, course=course)

            # 检查并从学生所属的共同体愿望课程中删除相应的课程
            for community in student.communities.all():
                wish_course_in_community = community.wish_courses.filter(pk=course_id).first()
                if wish_course_in_community:
                    community.wish_courses.remove(wish_course_in_community)

    @staticmethod
    def remove_wish_course(student_id, course_id):
        """
        删除学生的愿望课程，并更新相关的共同体愿望课程列表。
        """
        with transaction.atomic():
            student = StudentRepository.get_student_by_id(student_id)
            course = Course.objects.get(pk=course_id)

            # 删除学生的愿望课程
            student.wish_courses.filter(pk=course_id).delete()

            # 获取学生所属的所有共同体
            student_communities = student.communities.all()

            # 遍历每个共同体，删除仅属于该学生的愿望课程
            for community in student_communities:
                # 检查是否有其他成员也将该课程标记为愿望课程
                other_wishes = WishCourse.objects.filter(
                    community=community,
                    course=course
                ).exclude(student=student)

                # 如果没有其他成员愿望此课程，那么从共同体愿望课程列表中移除
                if not other_wishes:
                    community.wish_courses.remove(course)
