# views/index.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from demo.repositories.course_repository import CourseRepository
from demo.repositories.student_repository import StudentRepository
from demo.repositories.community_repository import CommunityRepository
from demo.views.operation.index import student_join_community, student_leave_community
from demo.views.recommend.index import get_recommended_communities
from demo.views.getInformation.index import get_student_list, get_community_list


def getinfo(request):
    data = json.loads(request.body.decode('utf-8'))
    who = data.get('type')
    ID = data.get('id')
    if who == 'community':
        community = CommunityRepository.get_community_by_id(ID)
        if not community:
            return JsonResponse({'error': 'community not found'}, status=404, safe=False)
        return get_community_list(community)
    elif who == 'student':
        student = StudentRepository.get_student_by_id(ID)
        if not student:
            return JsonResponse({'error': 'Student not found'}, status=404, safe=False)
        return get_student_list(student)  # 使用之前定义的 get_student_list 函数
    else:
        return JsonResponse({'error': 'Wrong type'}, safe=False)


@require_http_methods(['GET', 'POST'])
def recommend_communities(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Method Not Allowed'}, status=405, safe=False)

    data = json.loads(request.body.decode('utf-8'))
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    # 使用StudentRepository和CourseRepository获取学生和课程实例
    try:
        wish_course = CourseRepository.get_course_by_id(course_id)
    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False)
    # 更新学生愿望课程
    try:
        StudentRepository.add_wish_course(student_id, course_id)
    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False)

    # 获取推荐的学习共同体
    recommended_communities = get_recommended_communities(student_id, wish_course.course_id)

    # 构造返回结果
    community_list = [
        {
            'id': community.id,
            'name': community.name,
            'description': community.description,
            'similarity': sim,
        } for sim, community in recommended_communities
    ]
    return JsonResponse(community_list, safe=False)


@require_http_methods(['GET', 'POST'])
def operation(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Method Not Allowed'}, status=405, safe=False)

    data = json.loads(request.body.decode('utf-8'))
    opera = data.get('operation')
    student_id = data.get('student_id')
    community_id = data.get('community_id')

    # 检查是否提供了必要的参数
    if not all([opera, student_id, community_id]):
        return JsonResponse({'error': 'Missing required parameters.'}, status=400)

    # 根据 operation 触发对应的操作
    if opera == 'join':
        try:
            student_join_community(student_id, community_id)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif opera == 'leave':
        try:
            student_leave_community(student_id, community_id)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid operation.'}, status=400)

    return JsonResponse({'message': 'Operation completed successfully.'})
