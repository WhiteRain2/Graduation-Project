# demo/repositories/community_repository.py
from django.core.exceptions import ValidationError
from django.db.models import Count
from demo.models import Student, Community, Course, CompletedCourse, WishCourse, CommunityCompletedCourse, \
    CommunityWishCourse, CourseSimilarity
from django.db import transaction


class CommunityRepository:
    @staticmethod
    def create_community(name, description):
        """
        创建新的共同体。
        """
        return Community.objects.create(name=name, description=description)

    @staticmethod
    def get_community_by_id(community_id):
        """
        通过 ID 获取共同体。
        """
        return Community.objects.get(pk=community_id)

    @staticmethod
    def update_community(community_id, **update_data):
        """
        更新特定共同体的信息。
        """
        Community.objects.filter(pk=community_id).update(**update_data)

    @staticmethod
    def add_member_to_community(community_id, student_id):
        """
        将学生添加到共同体成员中。在添加前检查共同体人数是否已满。
        """
        community = CommunityRepository.get_community_by_id(community_id)
        student = Student.objects.get(pk=student_id)

        # 获取共同体当前成员数
        member_count = community.members.count()

        # 检查共同体人数是否已满
        if member_count >= Community.MAX_MEMBERS:
            raise ValidationError(f"The community with id {community_id} is full.")

        # 将学生添加到共同体
        community.members.add(student)
        # 开始更新共同体的已完成课程和愿望课程
        # 获取该学生的已完成课程和愿望课程
        student_completed_courses = set(student.completed_courses.all())
        student_wish_courses = set(student.wish_courses.all())
        # 获取共同体的已完成课程和愿望课程
        community_completed_courses = set(community.completed_courses.all())
        community_wish_courses = set(community.wish_courses.all())
        # 更新操作
        updated_completed_courses = community_completed_courses.union(student_completed_courses)
        updated_wish_courses = community_wish_courses.union(student_wish_courses) - updated_completed_courses

        # 添加课程到更新后的列表中
        for course in updated_completed_courses:
            CommunityCompletedCourse.objects.get_or_create(community=community, course=course)
        for course in updated_wish_courses:
            CommunityWishCourse.objects.get_or_create(community=community, course=course)

        # 删除不在更新后列表中的课程
        community.completed_courses.exclude(pk__in=[course.pk for course in updated_completed_courses]).delete()
        community.wish_courses.exclude(pk__in=[course.pk for course in updated_wish_courses]).delete()

    @staticmethod
    def add_completed_course_to_community(community_id, course_id):
        """
        添加课程到共同体的已完成课程。
        """
        community = CommunityRepository.get_community_by_id(community_id)
        course = Course.objects.get(pk=course_id)
        CompletedCourse.objects.create(community=community, course=course)

    @staticmethod
    def add_wish_course_to_community(community_id, course_id):
        """
        将课程添加到共同体的愿望课程。
        """
        community = CommunityRepository.get_community_by_id(community_id)
        WishCourse.objects.create(community=community, course_id=course_id)

    @staticmethod
    def remove_member_from_community(community_id, student_id):
        """
        从共同体中删除成员，并且删除该学生在共同体中独有的已完成课程和愿望课程。
        """

        community = CommunityRepository.get_community_by_id(community_id)
        student = Student.objects.get(pk=student_id)

        if community.members.count() <= 1:
            raise ValidationError(f"The community with id {community_id} cannot have zero members.")

        # 开启事务保证操作的原子性
        with transaction.atomic():
            # 删除成员
            community.members.remove(student)

            # 找出该学生独有的已完成课程和愿望课程
            unique_completed_courses = community.completed_courses \
                .annotate(num_students=Count('students_completed')) \
                .filter(students_completed=student, num_students=1)

            unique_wish_courses = community.wish_courses \
                .annotate(num_students=Count('students_wishing')) \
                .filter(students_wishing=student, num_students=1)

            # 删除这些独有的课程
            for course in unique_completed_courses:
                community.completed_courses.remove(course)

            for course in unique_wish_courses:
                community.wish_courses.remove(course)

    @staticmethod
    def remove_completed_course_from_community(community_id, course_id):
        """
        从共同体的已完成课程中删除指定的课程。
        """
        community = CommunityRepository.get_community_by_id(community_id)
        community.completed_courses.remove(Course.objects.get(pk=course_id))

    @staticmethod
    def remove_wish_course_from_community(community_id, course_id):
        """
        从共同体的愿望课程中删除指定的课程。
        """
        community = CommunityRepository.get_community_by_id(community_id)
        community.wish_courses.remove(Course.objects.get(pk=course_id))

    @staticmethod
    def get_eligible_communities_for_recommendation(student_id, current_wish_course_id,
                                                    max_members=Community.MAX_MEMBERS):
        """
        获取符合条件的共同体，即学生未加入、成员数小于MAX_MEMBERS，并且有学生愿望课程相似课程的共同体。
        :param student_id: 学生的唯一标识符
        :param current_wish_course_id: 学生当前愿望课程的课程ID
        :param max_members: 共同体允许的最大成员数
        :return: QuerySet, 符合条件的共同体列表
        """
        # 获取当前愿望课程的相似课程ID列表
        similar_course_ids = [k for k, v in
                              CourseSimilarity.objects.get(course_id=current_wish_course_id).similarity_vector.items()
                              if float(v) > 0]

        # 增加当前愿望课程ID到相似课程ID列表
        similar_course_ids.append(current_wish_course_id)

        # 获取符合条件的共同体列表
        eligible_communities = Community.objects.annotate(
            member_count=Count('members')
        ).filter(
            member_count__lt=max_members,
            completed_courses__course_id__in=similar_course_ids
        ).exclude(
            members__student_id=student_id
        ).distinct()

        return eligible_communities