# views/recommend/index.py
import json
from django.db.models import Prefetch, Avg
from demo.models import CourseSimilarity, CommunityCompletedCourse, CommunityWishCourse
from demo.repositories.community_repository import CommunityRepository
from demo.repositories.student_repository import StudentRepository
from concurrent.futures import ThreadPoolExecutor, as_completed


class CommunityRecommender:
    LOW_ENTER_THRESHOLD = 0.05  # 准入阈值

    def __init__(self, student_id, current_wish_course_id, max_communities=10, max_workers=4):
        self.student_id = student_id
        self.current_wish_course_id = current_wish_course_id
        self.max_communities = max_communities
        self.max_workers = max_workers
        self.course_similarity_data = self.load_course_similarities()
        self.student = StudentRepository.get_student_by_id(student_id)
        self.communities = CommunityRepository.get_eligible_communities_for_recommendation(
            student_id, current_wish_course_id
        ).prefetch_related(
            Prefetch('completed_courses'),
            Prefetch('wish_courses')
        )

    @staticmethod
    def load_course_similarities():
        """预先加载所有课程的相似度数据到内存"""
        course_similarities = CourseSimilarity.objects.all()
        course_similarity_data = {
            course_sim.course_id: course_sim.similarity_vector
            for course_sim in course_similarities
        }
        return course_similarity_data

    def get_courses_similarity(self, student_course_ids, community_course_data):
        total_similarity = 0
        comparisons = 0  # 记录比较的次数以计算平均值

        for course_a_id in student_course_ids:
            for course_b_data in community_course_data:
                if course_a_id == course_b_data['id']:
                    total_similarity += course_b_data['member_ratio']
                    comparisons += 1
                else:
                    # 使用预加载的相似度数据代替数据库查询
                    similarity_vector = self.course_similarity_data.get(course_a_id, {})
                    similarity = json.loads(similarity_vector).get(str(course_b_data['id']), 0)
                    # 仅在存在实际相似度数据时增加比较次数
                    if similarity > 0:
                        similarity *= course_b_data['member_ratio']
                        total_similarity += similarity
                        comparisons += 1

        # 避免除以0，如果没有任何比较发生，则返回0
        return total_similarity / comparisons if comparisons else 0

    def evaluate_course_similarity(self, community):
        student_wish_course_ids = self.student.wish_courses.values_list('course_id', flat=True)
        if self.current_wish_course_id not in student_wish_course_ids:
            return -1
        com_completed_course_data = [{
            'id': ccc.course.course_id,
            'member_ratio': ccc.member_ratio
        } for ccc in CommunityCompletedCourse.objects.filter(community=community)]
        com_wish_course_data = [{
            'id': ccc.course.course_id,
            'member_ratio': ccc.member_ratio
        } for ccc in CommunityWishCourse.objects.filter(community=community)]

        # Calculate the similarity score for the current wish course with the set of completed courses
        wish_course_similarity = self.get_courses_similarity([self.current_wish_course_id],
                                                             com_completed_course_data)

        # Calculate the similarity score for the set of completed student courses with the community's wish courses
        completed_course_similarity = 0
        if self.student.completed_courses.exists():
            student_completed_course_ids = self.student.completed_courses.values_list('course_id', flat=True)
            completed_course_similarity = self.get_courses_similarity(student_completed_course_ids, com_wish_course_data)

        final_similarity_score = 0.5 * wish_course_similarity + 0.5 * completed_course_similarity
        return final_similarity_score

    def evaluate_student_similarity(self, community):
        # 假设学生已加入社区中，计算新的性别比例
        hypothetical_male_count = community.members.filter(gender=1).count()
        if self.student.gender == 1:
            hypothetical_male_count += 1
        hypothetical_total_count = community.members.count() + 1 - community.members.filter(gender=2).count()
        new_gender_ratio = hypothetical_male_count / hypothetical_total_count if hypothetical_total_count > 0 else 0.5

        # 计算性别均衡性（0表示完全不均衡，1表示完全均衡）
        gender_balance = min(new_gender_ratio, 1 - new_gender_ratio) * 2

        # 计算新的学习风格多样性
        hypothetical_learning_styles = list(community.members.values_list('learning_style', flat=True))
        hypothetical_learning_styles.append(self.student.learning_style)
        count_sum = len(hypothetical_learning_styles)
        learning_style_distribution = [hypothetical_learning_styles.count(style) / count_sum for style in
                                       set(hypothetical_learning_styles)]
        new_learning_style_diversity = 1 - sum([x ** 2 for x in learning_style_distribution])

        # 计算新的活跃度平均值
        new_activity_level = (community.members.aggregate(Avg('activity_level'))[
                                  'activity_level__avg'] * community.members.count()
                              + self.student.activity_level) / hypothetical_total_count

        # 计算活跃度均衡性（假设0.5是最理想的平均活跃度）
        activity_balance = 1 - abs(new_activity_level - 0.5) / 0.5

        # 综合性别均衡、学习风格多样性和活跃度均衡来计算总相似度
        # 三个特征的权重可以根据实际情况调整，这里我们假设它们权重相等
        similarity_score = (gender_balance + new_learning_style_diversity + activity_balance) / 3

        return similarity_score

    def evaluate_similarity(self, community):
        c = self.evaluate_course_similarity(community)
        s = self.evaluate_student_similarity(community)
        return 0.4 * c + 0.6 * s, c, s

    def recommend_communities(self):
        recommended_communities = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_community = {
                executor.submit(self.evaluate_similarity, community): community
                for community in self.communities
            }

            for future in as_completed(future_to_community):
                community = future_to_community[future]
                try:
                    similarity_score = future.result()
                    if similarity_score[0] > self.LOW_ENTER_THRESHOLD:
                        recommended_communities.append((similarity_score, community))
                except Exception as exc:
                    print(f'Community {community.id} generated an exception: {exc}')

        recommended_communities.sort(key=lambda x: x[0][0], reverse=True)
        return recommended_communities[:self.max_communities]
