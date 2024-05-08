from django.core.management.base import BaseCommand, CommandError
import csv
import random
from django.db.models import F
from demo.models import Student, Community, Course, CompletedCourse, CommunityCompletedCourse
import time

class Command(BaseCommand):
    help = 'Import student data from CSV files and randomize attributes.'

    def handle(self, *args, **options):
        start_time = time.time()
        scores_csv_file_path = 'demo/static/scores.csv'
        students_activity_and_styles_csv_file_path = 'demo/static/students_activity_and_styles.csv'
        learning_style_mapping = {'未知': 0, '发散型': 1, '同化型': 2, '聚敛型': 3, '顺应型': 4}
        discarded_count = 0
        students_updated_count = 0
        communities_updated_count = 0

        # 更新学生的活动水平和学习风格等信息
        try:
            # 处理活动水平和学习风格的CSV文件
            self.stdout.write("开始处理学生活动水平和学习风格的CSV文件...")
            with open(students_activity_and_styles_csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    student_id = int(row['userId'])
                    learning_style = learning_style_mapping.get(row['LearningStyle'], 0)
                    activity_level_str = row['ActivityLevel']

                    try:
                        activity_level = float(activity_level_str) if activity_level_str else 0.5
                    except ValueError:
                        activity_level = 0.5
                        discarded_count += 1  # 记录无法转换的记录

                    student, created = Student.objects.get_or_create(
                        student_id=student_id,
                        defaults={
                            'learning_style': learning_style,
                            'activity_level': activity_level,
                        }
                    )

                    if not created:
                        student.learning_style = learning_style
                        student.activity_level = max(0.0, min(1.0, activity_level))
                        students_updated_count += 1

                    student.gender = random.choice([0, 1])
                    student.save()

            self.stdout.write(self.style.SUCCESS(
                f"完成学生活动水平和学习风格信息的导入，更新了 {students_updated_count} 名学生的信息。"))

            # 处理分数的CSV文件
            self.stdout.write("开始处理学生分数的CSV文件...")
            with open(scores_csv_file_path, newline='') as csvfile:
                data_reader = csv.DictReader(csvfile)
                for row in data_reader:
                    student, student_created = Student.objects.get_or_create(
                        student_id=int(row['userId'])
                    )

                    course, course_created = Course.objects.get_or_create(
                        course_id=int(row['courseId'])
                    )

                    if course_created:
                        course.name = f"Course {row['courseId']}"
                        course.description = "Course description here."
                        course.save()

                    comp_course, comp_course_created = CompletedCourse.objects.get_or_create(
                        student=student,
                        course=course,
                        defaults={'score': float(row['score'])}
                    )

                    if not comp_course_created:
                        comp_course.score = float(row['score'])
                        comp_course.save()

                    community, community_created = Community.objects.get_or_create(
                        name=f"Community for Student {row['userId']}")
                    if community_created:
                        community.description = f"Community description here."
                        community.save()

                    student.communities.add(community)
                    CommunityCompletedCourse.objects.get_or_create(
                        community=community,
                        course=course
                    )

                    student.save()
                    community.save()
                    if student_created or community_created:
                        communities_updated_count += 1

            self.stdout.write(self.style.SUCCESS(f'完成学生分数的处理，共更新了 {communities_updated_count} 个社群。'))
            self.stdout.write(self.style.SUCCESS(f'由于学生不存在而丢弃的记录数量为 {discarded_count}。'))

            # 更新社群的所有属性
            self.stdout.write("开始更新社群的所有属性...")
            for community in Community.objects.all():
                community.update_all_attributes()

            self.stdout.write(self.style.SUCCESS(f"完成社群属性更新。"))

            self.stdout.write(self.style.SUCCESS(f"数据导入和更新成功完成。"))
            end_time = time.time()  # 脚本结束时的时间
            execution_time = end_time - start_time  # 计算执行时间
            self.stdout.write(self.style.SUCCESS(f"数据导入和更新成功完成。总执行时间：{execution_time:.2f}秒。"))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'CSV文件未找到。请确保路径是正确的。 {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'处理过程中出现错误：{e}'))