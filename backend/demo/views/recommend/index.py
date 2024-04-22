# views/recommend/index.py

from django.db.models import Prefetch
from demo.models import CourseSimilarity, Student, Community
from demo.repositories.community_repository import CommunityRepository
from demo.repositories.student_repository import StudentRepository
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_course_similarities():
    """预先加载所有课程的相似度数据到内存"""
    course_similarities = CourseSimilarity.objects.all()
    course_similarity_data = {
        course_sim.course_id: course_sim.similarity_vector
        for course_sim in course_similarities
    }
    return course_similarity_data


def get_courses_similarity(course_similarity_data, course_a_ids, course_b_ids):
    # 如果两个列表中的课程ID完全相同，则直接返回1
    if set(course_a_ids) == set(course_b_ids):
        return 1

    total_similarity = 0
    comparisons = 0  # 记录比较的次数以计算平均值

    for course_a_id in course_a_ids:
        for course_b_id in course_b_ids:
            if course_a_id == course_b_id:
                total_similarity += 1
                comparisons += 1
            else:
                # 使用预加载的相似度数据代替数据库查询
                similarity_vector = course_similarity_data.get(course_a_id, {})
                similarity = similarity_vector.get(str(course_b_id), 0)
                total_similarity += similarity
                # 仅在存在实际相似度数据时增加比较次数
                if similarity > 0:
                    comparisons += 1

    # 避免除以0，如果没有任何比较发生，则返回0
    return total_similarity / comparisons if comparisons else 0


def evaluate_member_similarity(community, student, current_wish_course_id, course_similarity_data):
    student_wish_course_ids = student.wish_courses.values_list('course_id', flat=True)
    if current_wish_course_id not in student_wish_course_ids:
        return -1

    completed_course_ids = community.completed_courses.values_list('course_id', flat=True)
    wish_course_ids = community.wish_courses.values_list('course_id', flat=True)

    # Calculate the similarity score for the current wish course with the set of completed courses
    wish_course_similarity = get_courses_similarity(course_similarity_data, [current_wish_course_id],
                                                    completed_course_ids)

    # Calculate the similarity score for the set of completed student courses with the community's wish courses
    completed_course_similarity = 0
    if student.completed_courses.exists():
        student_completed_course_ids = student.completed_courses.values_list('course_id', flat=True)
        completed_course_similarity = get_courses_similarity(course_similarity_data, student_completed_course_ids,
                                                             wish_course_ids)

    final_similarity_score = 0.5 * wish_course_similarity + 0.5 * completed_course_similarity
    return final_similarity_score


def get_recommended_communities(student_id, current_wish_course_id, MAX_COMMUNITIES=10, testing=False, max_workers=4):
    student = StudentRepository.get_student_by_id(student_id)
    communities = (CommunityRepository.get_eligible_communities_for_recommendation(student_id, current_wish_course_id)
    .prefetch_related(
        Prefetch('completed_courses'),
        Prefetch('wish_courses')
    ))
    if testing:
        return [(0, community) for community in communities[:MAX_COMMUNITIES]]

    course_similarity_data = load_course_similarities()
    # 设置准入阈值
    LOW_ENTER_THRESHOLD = 0.05
    recommended_communities = []

    # 使用线程池并行计算每个社区的相似度分数
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_community = {executor.submit(evaluate_member_similarity, community, student, current_wish_course_id,
                                               course_similarity_data): community for community in communities}

        for future in as_completed(future_to_community):
            community = future_to_community[future]
            try:
                similarity_score = future.result()
                if similarity_score > LOW_ENTER_THRESHOLD:
                    recommended_communities.append((similarity_score, community))
            except Exception as exc:
                print(f'Community {community.id} generated an exception: {exc}')

    recommended_communities.sort(key=lambda x: x[0], reverse=True)
    recommended_communities = recommended_communities[:MAX_COMMUNITIES]

    return recommended_communities