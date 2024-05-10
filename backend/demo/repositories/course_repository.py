# demo/repositories/course_repository.py
from django.core.exceptions import ObjectDoesNotExist
from demo.models import Course, CourseChapter, CourseTask


class CourseRepository:
    @staticmethod
    def create_course(**course_data):
        """
        创建新的课程记录。
        """
        return Course.objects.create(**course_data)

    @staticmethod
    def get_course_by_id(course_id):
        """
        根据 ID 获取课程记录。
        """
        try:
            return Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise ValueError("Course Not Exist")

    @staticmethod
    def update_course(course_id, **update_data):
        """
        更新特定课程的信息。
        """
        Course.objects.filter(pk=course_id).update(**update_data)

    @staticmethod
    def get_all_courses():
        """
        获取所有课程的列表。
        """
        return Course.objects.all()

    @staticmethod
    def get_chapters_by_course(course_id):
        """
        根据课程ID获取所有相关章节信息。
        """
        try:
            course = Course.objects.get(pk=course_id)
            return course.chapters.all().order_by('seq')
        except Course.DoesNotExist:
            raise ValueError("Course Not Exist")

    @staticmethod
    def get_tasks_by_course(course_id):
        """
        根据课程ID获取所有相关任务信息。
        """
        try:
            course = Course.objects.get(pk=course_id)
            return course.tasks.all().order_by('seq')
        except Course.DoesNotExist:
            raise ValueError("Course Not Exist")