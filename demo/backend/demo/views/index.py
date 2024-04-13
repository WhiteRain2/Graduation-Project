# views.py

import json
from django.shortcuts import get_object_or_404
from demo.models import Student, Course, WishCourse, Community, CourseSimilarity
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


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


def evaluate_member_similarity(community, student, current_wish_course_id, course_similarity):
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
            course_a_similarity_obj = course_similarity.get(course_id=course_a_id)
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
        for community_course in community.completed_courses.all()
    ) / max(1, community.completed_courses.count())  # 避免除以零

    # 同样的方法，计算学生已完成课程与共同体愿望课程列表的相似度
    completed_course_similarity = sum(
        calculate_course_similarity(student_course.course_id, wish_course.course_id)
        for student_course in student.completed_courses.all()
        for wish_course in community.wish_courses.all()
    ) / max(1, (student.completed_courses.count() * community.wish_courses.count()))  # 避免除以零

    # 最终相似度评分是两部分匹配度的加权平均
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
    communities = Community.objects.all()
    recommended_communities = []
    course_similarity = CourseSimilarity.objects
    for community in communities:
        if student in community.members.all() or community.members.count() >= community.MAX_MEMBERS:
            continue
        # 计算学生与每个共同体的相似度评分
        similarity_score = evaluate_member_similarity(community, student, current_wish_course_id, course_similarity)
        # 编织推荐列表
        if len(recommended_communities) < MAX_COMMUNITIES:
            recommended_communities.append((similarity_score, community))
        else:
            # 找到并替换最低相似度的共同体
            lowest_scored_community = min(recommended_communities, key=lambda x: x[0])
            if similarity_score > lowest_scored_community[0]:
                recommended_communities.remove(lowest_scored_community)
                recommended_communities.append((similarity_score, community))
    # 根据相似度评分对共同体列表进行排序
    recommended_communities.sort(key=lambda x: x[0], reverse=True)
    return recommended_communities


@require_http_methods(['GET', 'POST'])
def recommend_communities(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        student_id = data.get('student_id')
        course_id = data.get('course_id')

        student = get_object_or_404(Student, student_id=student_id)
        wish_course = get_object_or_404(Course, course_id=course_id)

        if wish_course in student.completed_courses.all():
            return JsonResponse({'error': 'Course Completed'}, safe=False)
        # 处理学生愿望课程，更新数据库
        update_student_wish_courses(student, wish_course)
        print('update student wish course')
        # 调用推荐算法接口获取推荐的学习共同体
        recommended_communities = get_recommended_communities(student, wish_course.course_id)
        print('recommended_communities')
        community_list = []
        # 将结果封装为JsonResponse
        for sim, community in recommended_communities:
            community_list.append({
                'id': community.id,
                'name': community.name,
                'description': community.description,
                'similarity': sim,
            })
        return JsonResponse(community_list, safe=False)

    return JsonResponse({'error': 'Error GET'}, safe=False)


def index(request):
    return recommend_communities(request)
