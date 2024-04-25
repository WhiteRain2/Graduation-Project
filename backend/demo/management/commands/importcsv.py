from django.core.management.base import BaseCommand, CommandError
import csv
import random
from django.db.models import F
from demo.models.student import Student
from demo.models.community import Community


class Command(BaseCommand):
    help = 'Import student style and activity level from a CSV file, then randomize gender and update community attributes.'

    def handle(self, *args, **options):
        csv_file_path = 'demo/static/students_activity_and_styles.csv'
        discarded_count = 0

        self.stdout.write("Starting the import process...")
        try:
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                # 学习风格映射
                learning_style_mapping = {'未知': 0, '发散型': 1, '同化型': 2, '聚敛型': 3, '顺应型': 4}

                for row in reader:
                    student_id = int(row['userId'])
                    learning_style = learning_style_mapping.get(row['LearningStyle'], 0)
                    # 在转换前检查ActivityLevel是否为空或非数值
                    activity_level_str = row['ActivityLevel']
                    try:
                        activity_level = float(activity_level_str)
                    except ValueError:  # 如果无法转换为浮点数，使用默认值0.5
                        activity_level = 0.5

                    try:
                        student = Student.objects.get(student_id=student_id)
                        student.learning_style = learning_style
                        student.activity_level = max(0.0, min(1.0, activity_level))
                        student.save()
                    except Student.DoesNotExist:
                        discarded_count += 1

            self.stdout.write(self.style.SUCCESS('Completed updating/verifying existing student records.'))

            # 遍历所有学生对象，随机赋值性别属性
            self.stdout.write("Randomizing gender of all students...")
            for student in Student.objects.all():
                student.gender = random.choice([0, 1])
                student.save()

            self.stdout.write(self.style.SUCCESS("Successfully randomized genders."))

            # 遍历所有共同体对象，执行update_all_attributes方法
            self.stdout.write("Updating all community attributes...")
            for community in Community.objects.all():
                community.update_all_attributes()

            self.stdout.write(self.style.SUCCESS('Successfully updated community attributes.'))
            self.stdout.write(self.style.SUCCESS(f'Discarded {discarded_count} records for non-existing students.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please make sure the path is correct.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))

    # 导入分数
    #help = '从CSV文件中导入成绩信息'
    # def handle(self, *args, **options):
    #     # 替换为您的CSV文件实际路径
    #     csv_file_path = 'demo/static/scores.csv'
    #
    #     # 打开CSV文件并读取内容
    #     with open(csv_file_path, newline='') as csvfile:
    #         data_reader = csv.DictReader(csvfile)
    #         for row in data_reader:
    #             # 获取或创建学生对象
    #             student, student_created = Student.objects.get_or_create(student_id=int(row['userId']))
    #
    #             # 通过course_id获取或创建课程对象
    #             course, course_created = Course.objects.get_or_create(course_id=int(row['courseId']))
    #
    #             if course_created:
    #                 # 如果创建了新课程，您可能需要额外填充其他课程信息，例如课程名称和描述
    #                 course.name = f"Course {row['courseId']}"
    #                 course.description = "Course description here."
    #                 course.save()
    #
    #             # 创建学生的已完成课程
    #             comp_course, comp_course_created = CompletedCourse.objects.get_or_create(
    #                 student=student,
    #                 course=course,
    #                 defaults={'score': float(row['score'])}
    #             )
    #
    #             if not comp_course_created:
    #                 # 如果已经创建了这个完成的课程，更新成绩
    #                 comp_course.score = float(row['score'])
    #                 comp_course.save()
    #
    #             # 创建或获取只包含该名学生的共同体对象
    #             community, community_created = Community.objects.get_or_create(
    #                 name=f"Community for Student {row['userId']}")
    #             if community_created:
    #                 # 如果创建了新的共同体，设置共同体的描述或其他相关属性
    #                 community.description = f"Community description here."
    #                 community.save()
    #
    #             # 将学生添加到共同体中，并确保共同体的已完成课程包含这名学生已经完成的课程
    #             student.communities.add(community)
    #
    #             # 对每个新创建的共同体，添加学生已经完成的课程
    #             CommunityCompletedCourse.objects.get_or_create(
    #                 community=community,
    #                 course=course
    #             )
    #
    #             # 保存学生和共同体对象
    #             student.save()
    #             community.save()
    #
    #     self.stdout.write(self.style.SUCCESS('成功导入CSV文件数据'))