# views/index.py
import json

from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from demo.models import Student, StudentProfile
from demo.repositories.course_repository import CourseRepository
from demo.repositories.student_repository import StudentRepository
from demo.repositories.community_repository import CommunityRepository
from demo.views.operation.index import student_join_community, student_leave_community
from demo.views.recommend.index import get_recommended_communities


@require_http_methods(['POST'])
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


@require_http_methods(['POST'])
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


@require_http_methods(['POST'])
@transaction.atomic
def regis(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not all([username, password, email]):
        return JsonResponse(
            {"error": "用户名，密码和邮箱都是必需的。"},
            status=400
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"error": "用户名已存在。"},
            status=400
        )

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    # 使用当前时间戳作为学生 ID
    student_id = int(timezone.now().timestamp())
    student = StudentRepository.create_student(student_id, username)

    student_profile = StudentProfile(user=user, student=student)
    student_profile.save()

    return JsonResponse({"success": "用户注册成功。"}, status=201)