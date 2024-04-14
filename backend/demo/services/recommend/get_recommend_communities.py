# services/recommend/recommend.py

from demo.models import Student, Course, WishCourse, Community, CourseSimilarity
from django.db.models import Count


def update_student_wish_courses(student, wish_course):
    if wish_course in student.wish_courses.all():
        return False
    if student.wish_courses.count() < Student.MAX_WISH_COURSES:
        # 将课程添加到学生的愿望课程中
        WishCourse.objects.create(student=student, course=wish_course)
    else:
        # 如果愿望课程已满，则替换最旧的愿望课程
        oldest_wish_course = student.wish_courses.order_by('wishcourse__timestamp').first()
        WishCourse.objects.filter(student=student, course=oldest_wish_course).delete()
        WishCourse.objects.create(student=student, course=wish_course)
    return True


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


def get_recommended_communities(student, current_wish_course_id, MAX_COMMUNITIES=10):
    """
    获取推荐的学习共同体列表。这个函数基于学生的当前愿望课程与共同体的匹配程度进行推荐，
    返回相似度最高的MAX_COMMUNITIES个共同体。

    :param student: 学生对象
    :param current_wish_course_id: 愿望课程对象id
    :param MAX_COMMUNITIES: 最大推荐数目
    :return: 推荐的学习共同体列表
    """
    # 获得共同体成员少于 MAX_MEMBERS 的共同体，排除学生当前已加入的
    communities = Community.objects.annotate(
        member_count=Count('members')
    ).filter(
        member_count__lt=Community.MAX_MEMBERS
    ).exclude(
        members__student_id=student.student_id
    )

    # 预加载共同体的愿望课程和完成课程以及课程相似度
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
