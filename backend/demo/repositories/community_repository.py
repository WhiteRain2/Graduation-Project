# demo/repositories/community_repository.py
import json

from django.core.exceptions import ValidationError
from django.db.models import Count
from demo.models import Student, Community, CourseSimilarity
from django.db import transaction


class CommunityRepository:

    @staticmethod
    def create_community(community_name):
        community = Community.objects.create(name=community_name)

    @staticmethod
    def get_community_by_id(community_id):
        """
        通过 ID 获取共同体。
        """
        return Community.objects.get(pk=community_id)

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
        # 调用方法更新共同体所有属性
        community.update_all_attributes()

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
            community.update_all_attributes()

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
        # 先得到相似度的JSON字符串
        similarity_vector_str = CourseSimilarity.objects.get(course_id=current_wish_course_id).similarity_vector

        # 将JSON字符串解析为字典
        similarity_vector_dict = json.loads(similarity_vector_str)

        # 筛选出相似度大于0的课程ID
        similar_course_ids = [k for k, v in similarity_vector_dict.items() if float(v) > 0]

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
