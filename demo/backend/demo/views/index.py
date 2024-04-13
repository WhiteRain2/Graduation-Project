# views.py

import json
from django.shortcuts import get_object_or_404
from demo.models import Student, Course, WishCourse, Community
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def update_student_wish_courses(student, wish_course):
    if student.wish_courses.count() < Student.MAX_WISH_COURSES:
        # 将课程添加到学生的愿望课程中
        WishCourse.objects.create(student=student, course=wish_course)
    else:
        # 如果愿望课程已满，则替换最旧的愿望课程
        oldest_wish_course = student.wish_courses.order_by('wishcourse__timestamp').first()
        WishCourse.objects.filter(student=student, course=oldest_wish_course).delete()
        WishCourse.objects.create(student=student, course=wish_course)

    return True


def get_recommended_communities(student, wish_course, MAX_COMMUNITIES=10):
    """
    获取推荐的学习共同体列表。这个函数应该由实际的推荐算法逻辑实现。
    现在暂时返回一个空列表，您需要用您的算法逻辑替换它。

    :param student: 学生对象
    :param wish_course: 愿望课程对象
    :return: 推荐的学习共同体列表
    """
    communities = Community.objects.all()
    recommended_communities = []
    for community in communities:
        if student in community.members.all() or community.members.count() >= community.MAX_MEMBERS:
            continue
        if len(recommended_communities) >= MAX_COMMUNITIES:
            break
        recommended_communities.append(community)
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

        # 调用推荐算法接口获取推荐的学习共同体
        recommended_communities = get_recommended_communities(student, wish_course)
        community_list = []
        # 将结果封装为JsonResponse
        for community in recommended_communities:
            community_list.append({
                'id': community.id,
                'name': community.name,
                'description': community.description,
            })
        return JsonResponse(community_list, safe=False)

    return JsonResponse({'error': 'Error GET'}, safe=False)


def index(request):
    return recommend_communities(request)
