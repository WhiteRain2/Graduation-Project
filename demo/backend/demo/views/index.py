# views.py

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from demo.models import Student, Course, WishCourse, Community


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


def get_recommended_communities(student, wish_course):
    """
    获取推荐的学习共同体列表。这个函数应该由实际的推荐算法逻辑实现。
    现在暂时返回一个空列表，您需要用您的算法逻辑替换它。

    :param student: 学生对象
    :param wish_course: 愿望课程对象
    :return: 推荐的学习共同体列表
    """
    communities = Community.objects.all()
    for community in communities:
        pass
    return []


def recommend_communities(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        student = get_object_or_404(Student, student_id=student_id)
        wish_course = get_object_or_404(Course, course_id=course_id)

        if wish_course in student.completed_courses.all():
            return render(request, '404.html')
        # 处理学生愿望课程，更新数据库
        update_student_wish_courses(student, wish_course)

        # 调用推荐算法接口获取推荐的学习共同体
        recommended_communities = get_recommended_communities(student, wish_course)

        # 将结果返回给前端
        return render(request, 'recommendation_results.html', {'communities': recommended_communities})

    return render(request, 'student_form.html')


def index(request):
    return render(request, 'student_form.html')