# demo/repositories/course_repository.py
from django.core.exceptions import ObjectDoesNotExist
from demo.models import Course


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
        except ObjectDoesNotExist:
            raise ValueError(f"Not Exist")

    @staticmethod
    def update_course(course_id, **update_data):
        """
        更新特定课程的信息。
        """
        Course.objects.filter(pk=course_id).update(**update_data)

