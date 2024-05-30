import random
from django.core.management.base import BaseCommand
from django.db import transaction
from demo.models.student import Student
from demo.models.course import Course
from demo.views.operation.index import student_join_community
from demo.views.recommend.community_recommender import CommunityRecommender


class Command(BaseCommand):
    help = 'Remo run'

    @transaction.atomic
    def handle(self, *args, **options):
        course_ids = list(Course.objects.values_list('course_id', flat=True))
        for student in Student.objects.all()[:500]:
            if student.communities.count() > 1:
                continue
            random_course_id = random.choice(course_ids)
            recommender = CommunityRecommender(student.student_id, random_course_id)
            recommended_communities = recommender.recommend_communities()

            # 随机选择加入0到4个共同体
            number_of_communities_to_join = random.randint(0, min(6, len(recommended_communities)))
            communities_to_join = random.sample(recommended_communities, number_of_communities_to_join)

            for _, community in communities_to_join:
                student_join_community(student.student_id, community.id)
            self.stdout.write(
                self.style.SUCCESS(f'Student {student.student_id} joined {len(communities_to_join)} communities'))

