from django.core.management.base import BaseCommand
import csv
from demo.models.student import Student
from demo.models.community import Community
from demo.models.course import Course
from demo.models.relations import CompletedCourse, CommunityCompletedCourse


class Command(BaseCommand):
    help = '从CSV文件中导入成绩信息'

    def handle(self, *args, **options):
        # 替换为您的CSV文件实际路径
        csv_file_path = 'demo/static/scores.csv'

        # 打开CSV文件并读取内容
        with open(csv_file_path, newline='') as csvfile:
            data_reader = csv.DictReader(csvfile)
            for row in data_reader:
                # 获取或创建学生对象
                student, student_created = Student.objects.get_or_create(student_id=int(row['userId']))

                # 通过course_id获取或创建课程对象
                course, course_created = Course.objects.get_or_create(course_id=int(row['courseId']))

                if course_created:
                    # 如果创建了新课程，您可能需要额外填充其他课程信息，例如课程名称和描述
                    course.name = f"Course {row['courseId']}"
                    course.description = "Course description here."
                    course.save()

                # 创建学生的已完成课程
                comp_course, comp_course_created = CompletedCourse.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={'score': float(row['score'])}
                )

                if not comp_course_created:
                    # 如果已经创建了这个完成的课程，更新成绩
                    comp_course.score = float(row['score'])
                    comp_course.save()

                # 创建或获取只包含该名学生的共同体对象
                community, community_created = Community.objects.get_or_create(
                    name=f"Community for Student {row['userId']}")
                if community_created:
                    # 如果创建了新的共同体，设置共同体的描述或其他相关属性
                    community.description = f"Community description here."
                    community.save()

                # 将学生添加到共同体中，并确保共同体的已完成课程包含这名学生已经完成的课程
                student.communities.add(community)

                # 对每个新创建的共同体，添加学生已经完成的课程
                CommunityCompletedCourse.objects.get_or_create(
                    community=community,
                    course=course
                )

                # 保存学生和共同体对象
                student.save()
                community.save()

        self.stdout.write(self.style.SUCCESS('成功导入CSV文件数据'))