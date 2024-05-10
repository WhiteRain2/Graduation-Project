import string
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from random import choices
from demo.models.student import Student
from demo.models.student_profile import StudentProfile


class Command(BaseCommand):
    help = 'Create User instances for each Student instance with synchronized name and relate them in the database.'

    def add_arguments(self, parser):
        # 可选：为命令添加参数
        pass

    def handle(self, *args, **options):
        students = Student.objects.all()

        # 随机生成学生名和用户名策略函数
        def generate_random_username():
            length = choices([3, 4, 5])[0]
            return ''.join(choices(string.ascii_letters, k=length))

        with transaction.atomic():
            for student in students:
                random_name = generate_random_username()

                # 确保生成的用户名是唯一的
                while User.objects.filter(username=random_name).exists():
                    random_name = generate_random_username()

                # 创建User对象并保存到数据库
                user = User.objects.create(
                    username=random_name,
                    email='example@example.com',
                    is_staff=False,
                    is_superuser=False
                )

                # 更新Student对象的name字段，并保存
                student.name = user.username
                student.save()

                # 创建并保存StudentProfile对象
                StudentProfile.objects.create(user=user, student=student)

                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" with student ID {student.student_id} created and linked.'))

        self.stdout.write(self.style.SUCCESS('All students have been processed.'))