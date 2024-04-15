# views/recommend/index.py

from demo.models import CourseSimilarity
from demo.repositories.community_repository import CommunityRepository
from demo.repositories.student_repository import StudentRepository


def get_courses_similarity(course_similarity_qs, course_a_ids, course_b_ids):
    # 如果两个列表中的课程ID完全相同，则直接返回1
    if set(course_a_ids) == set(course_b_ids):
        return 1
    if len(course_a_ids) == 1 and course_a_ids[0] in course_b_ids:
        return 1
    if len(course_b_ids) == 1 and course_b_ids[0] in course_a_ids:
        return 1

    total_similarity = 0
    comparisons = 0  # 记录比较的次数以计算平均值

    for course_a_id in course_a_ids:
        for course_b_id in course_b_ids:
            if course_a_id == course_b_id:
                total_similarity += 1
                comparisons += 1
            else:
                try:
                    course_similarity_obj = course_similarity_qs.get(course__course_id=course_a_id)
                    similarity = course_similarity_obj.similarity_vector.get(str(course_b_id), 0)
                    total_similarity += similarity
                    # 仅在存在实际相似度数据时增加比较次数
                    if similarity > 0:
                        comparisons += 1
                except CourseSimilarity.DoesNotExist:
                    continue

    # 避免除以0，如果没有任何比较发生，则返回0
    return total_similarity / comparisons if comparisons else 0


def evaluate_member_similarity(community, student, current_wish_course_id, course_similarity_qs):
    """
    根据学生的当前愿望课程以及已完成课程与共同体完成的课程和愿望课程
    列表相匹配的程度，计算学生与共同体的相似度评分。
    :param community: community, 共同体实例
    :param student: Student, 学生实例
    :param current_wish_course_id: int, 学生当前的愿望课程ID
    :param course_similarity_qs: 课程相似度表查询
    :return: float, 学生与共同体的相似度评分
    """
    student_wish_course_ids = student.wish_courses.values_list('course_id', flat=True)
    if current_wish_course_id not in student_wish_course_ids:
        return -1

    completed_course_ids = community.completed_courses.values_list('course_id', flat=True)
    wish_course_ids = community.wish_courses.values_list('course_id', flat=True)

    # Calculate the similarity score for the current wish course with the set of completed courses
    wish_course_similarity = get_courses_similarity(course_similarity_qs, [current_wish_course_id],
                                                    completed_course_ids)

    # Calculate the similarity score for the set of completed student courses with the community's wish courses
    completed_course_similarity = 0
    if student.completed_courses.exists():
        student_completed_course_ids = student.completed_courses.values_list('course_id', flat=True)
        completed_course_similarity = get_courses_similarity(course_similarity_qs, student_completed_course_ids,
                                                             wish_course_ids)

    final_similarity_score = 0.5 * wish_course_similarity + 0.5 * completed_course_similarity
    return final_similarity_score


def get_recommended_communities(student_id, current_wish_course_id, MAX_COMMUNITIES=10):
    student = StudentRepository.get_student_by_id(student_id)
    # 调用CommunityRepository中的方法获取推荐共同体
    communities = CommunityRepository.get_eligible_communities_for_recommendation(student_id)

    # 相似度查询保持不变
    course_similarity_qs = CourseSimilarity.objects.select_related('course').only('course__course_id',
                                                                                  'similarity_vector')

    recommended_communities = []
    for community in communities:
        similarity_score = evaluate_member_similarity(community, student, current_wish_course_id, course_similarity_qs)

        if len(recommended_communities) < MAX_COMMUNITIES:
            recommended_communities.append((similarity_score, community))
        else:
            lowest_scored_community = min(recommended_communities, key=lambda x: x[0])
            if similarity_score > lowest_scored_community[0]:
                recommended_communities.remove(lowest_scored_community)
                recommended_communities.append((similarity_score, community))

    recommended_communities.sort(key=lambda x: x[0], reverse=True)
    return recommended_communities
