# views/getInformation/index.py
from demo.models import CompletedCourse, WishCourse
from django.http import JsonResponse


def get_student_list(student):
    # 获取已完成的课程
    completed_courses_json = [{'id': cc.course.course_id, 'name': cc.course.name, 'score': cc.score}
                              for cc in CompletedCourse.objects.filter(student=student)]

    # 获取愿望课程
    wish_courses_json = [{'id': wc.course.course_id, 'name': wc.course.name}
                         for wc in WishCourse.objects.filter(student=student)]

    # 获取已加入的共同体
    communities_json = [{'id': c.id, 'name': c.name, 'description': c.description}
                        for c in student.communities.all()]

    # 返回 JSON 响应
    return JsonResponse({
        'id': student.student_id,
        'name': student.name,
        'completed_courses': completed_courses_json,
        'wish_courses': wish_courses_json,
        'communities': communities_json,
    })
