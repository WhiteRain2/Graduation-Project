# views/index.py

import json
from django.shortcuts import get_object_or_404
from demo.models import Student, Course, WishCourse, Community, CourseSimilarity
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from demo.views.getInformation.index import get_student_list

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


def index(request, userId):
    student = get_object_or_404(Student, student_id=userId)
    if not student:
        return JsonResponse({'error': 'Student not found'}, safe=False)
    return get_student_list(student)  # 使用之前定义的 get_student_list 函数

