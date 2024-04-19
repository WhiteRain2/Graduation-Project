from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from demo.models.student import Student
from demo.models.student_profile import StudentProfile


class Command(BaseCommand):
    help = 'Synchronizes Student instances with corresponding User instances and updates student names.'

    def add_arguments(self, parser):
        # 可选: 为命令添加参数来指定默认密码或其他选项
        parser.add_argument('--default-password', type=str, help='Default password for created users')

    def handle(self, *args, **options):
        default_password = options.get('default_password', '123456')  # 设置默认密码
        with transaction.atomic():
            for student in Student.objects.all():
                user = User.objects.create(
                    email='example@example.com',
                    is_staff=False,
                    is_superuser=False
                )
                # 创建组合后的用户名
                new_username = f'{student.name}_{user.id}'
                user.username = new_username
                user.set_password(default_password)  # 设置加密的默认密码
                user.save()

                # 创建用户配置文件
                StudentProfile.objects.create(user=user, student=student)

                # 更新Student实例的name字段为我们的new_username或其他逻辑生成的name
                student.name = new_username  # 或是其他逻辑生成的name
                student.save()  # 保存更改

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created user and profile for student {new_username} and updated student name.'))

        self.stdout.write(self.style.SUCCESS('All students have been processed.'))