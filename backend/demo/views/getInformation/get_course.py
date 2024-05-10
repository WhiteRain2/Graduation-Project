from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from demo.repositories.course_repository import CourseRepository


@require_http_methods(["GET"])
def get_course_info(request, course_id):
    """
    获取课程详细信息的API接口。
    """
    try:
        course = CourseRepository.get_course_by_id(course_id)
        chapters = CourseRepository.get_chapters_by_course(course_id)
        tasks = CourseRepository.get_tasks_by_course(course_id)

        # 序列化课程信息
        course_data = {
            'course_id': course.course_id,
            'name': course.name,
            'description': course.description
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