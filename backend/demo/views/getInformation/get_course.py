from django.core.exceptions import ValidationError
from django.core.validators import validate_integer
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods

from demo.models import Course, Student, CompletedCourse, WishCourse
from demo.repositories.course_repository import CourseRepository


@require_http_methods(["GET"])
def get_course_info(request):
    """
    获取课程详细信息的API接口。
    """
    try:
        course_id = request.GET["course_id"]
        course = CourseRepository.get_course_by_id(course_id)
        chapters = CourseRepository.get_chapters_by_course(course_id)
        tasks = CourseRepository.get_tasks_by_course(course_id)

        completed_students_count = CompletedCourse.objects.filter(course=course).count()
        wish_students_count = WishCourse.objects.filter(course=course).count()
        total_count = completed_students_count + wish_students_count

        # 序列化课程信息
        course_data = {
            'course_id': course.course_id,
            'name': course.name,
            'photo': course.photo,
            'teachers': course.teachers,
            'created_time': course.created_time,
            'total_count': total_count,
            'description': course.description,
        }

        # 序列化章节信息
        chapters_data = [
            {
                'type': chapter.type,
                'number': chapter.number,
                'seq': chapter.seq,
                'title': chapter.title,
                'created_time': chapter.created_time,
                'updated_time': chapter.updated_time,
                'status': chapter.get_status_display(),
                'is_optional': chapter.is_optional
            }
            for chapter in chapters
        ]

        # 序列化任务信息
        tasks_data = [
            {
                'seq': task.seq,
                'activity_id': task.activity_id,
                'title': task.title,
                'is_free': task.is_free,
                'is_optional': task.is_optional,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'type': task.get_type_display(),
                'status': task.get_status_display(),
                'created_time': task.created_time,
                'updated_time': task.updated_time
            }
            for task in tasks
        ]

        # 将课程信息、章节和任务合并到单个JSON中
        response_data = {
            'course': course_data,
            'chapters': chapters_data,
            'tasks': tasks_data
        }

        return JsonResponse(response_data)

    except ValueError as e:
        # 捕获由CourseRepository抛出的不存在异常
        return JsonResponse({'error': str(e)}, status=404)


def search_courses(request):
    if request.method == 'GET':
        try:
            keyword = request.GET.get('keyword', '')
            ct = int(request.GET.get('ct', 0))  # 获取匹配结果的数量限制
        except (ValueError):
            return JsonResponse({'error': 'Invalid parameter format'}, status=400)

        try:
            # 尝试验证关键词是否为整数
            validate_integer(keyword)
            is_number = True
        except ValidationError:
            is_number = False

        if is_number:
            # 如果keyword为数字，查找以该数字开头的所有课程id
            courses = Course.objects.filter(course_id__startswith=keyword)
        else:
            # 如果keyword为非数字，按课程名进行搜索
            courses = Course.objects.filter(name__icontains=keyword)

        if not courses.exists():
            return JsonResponse({'error': 'No matching results found'}, status=404)

        courses = courses[:ct] if ct > 0 else courses  # 根据ct参数限制返回结果数量

        # 序列化查询结果
        courses_data = [{
            'course_id': course.course_id,
            'name': course.name,
            'description': course.description,
            'teachers': course.teachers,
            'created_time': course.created_time,
        } for course in courses]

        return JsonResponse({'courses': courses_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    