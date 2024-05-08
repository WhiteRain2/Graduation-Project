import csv
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now
from demo.models.course import Course, CourseChapter, CourseTask


class Command(BaseCommand):
    help = 'Imports course chapters and tasks from CSV files using bulk operations for performance'

    def add_arguments(self, parser):
        parser.add_argument('course_chapters_csv', type=str)
        parser.add_argument('course_tasks_csv', type=str)

    def handle(self, *args, **options):
        self.stdout.write("开始导入课程章节...")
        self.import_course_chapters(options['course_chapters_csv'])
        self.stdout.write("完成课程章节的导入。\n开始导入课程任务...")
        self.import_course_tasks(options['course_tasks_csv'])
        self.stdout.write("完成课程任务的导入。")

    def parse_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return -1

    def parse_time(self, timestamp_str):
        try:
            return int(timestamp_str)
        except (ValueError, TypeError):
            return int(time.mktime(now().timetuple()))

    @transaction.atomic
    def import_course_chapters(self, course_chapters_csv):
        chapters_to_create = []
        course_ids = set(Course.objects.values_list('course_id', flat=True))
        skipped_count = 0
        with open(course_chapters_csv, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                course_id = self.parse_int(row.get('courseId'))
                if course_id not in course_ids:
                    skipped_count += 1
                    self.stdout.write(f"跳过课程ID {course_id} 的章节，因为它不存在于数据库中。")
                    continue

                created_time = self.parse_time(row.get('createdTime'))
                updated_time = self.parse_time(row.get('updatedTime'))

                chapter = CourseChapter(
                    course_id=course_id,  # Directly assign the course_id
                    type=row.get('type', 'unknown') if row.get('type') in dict(
                        CourseChapter.TYPE_CHOICES).keys() else 'unknown',
                    number=self.parse_int(row.get('number')),
                    seq=self.parse_int(row.get('seq')),
                    title=row['title'],
                    created_time=created_time,
                    updated_time=updated_time,
                    status=row.get('status', 'unknown') if row.get('status') in dict(
                        CourseChapter.STATUS_CHOICES).keys() else 'unknown',
                    is_optional=bool(self.parse_int(row.get('isOptional')) in [True, 1])
                )

                chapters_to_create.append(chapter)
                if (i + 1) % 1000 == 0:
                    self.stdout.write(f"已处理 {i + 1} 行课程章节数据...")

        CourseChapter.objects.bulk_create(chapters_to_create, batch_size=1000)
        self.update_course_names(chapters_to_create)
        self.stdout.write(f"成功导入 {len(chapters_to_create)} 条课程章节数据。跳过 {skipped_count} 条数据。")

    def update_course_names(self, chapters):
        for chapter in chapters:
            if chapter.seq == 1 and chapter.type == 'chapter':
                Course.objects.filter(course_id=chapter.course_id).update(name=chapter.title)

    @transaction.atomic
    def import_course_tasks(self, course_tasks_csv):
        tasks_to_create = []
        course_ids = set(Course.objects.values_list('course_id', flat=True))
        skipped_count = 0
        with open(course_tasks_csv, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                course_id = self.parse_int(row.get('courseId'))
                if course_id not in course_ids:
                    skipped_count += 1
                    self.stdout.write(f"跳过课程ID {course_id} 的任务，因为它不存在于数据库中。")
                    continue

                start_time = self.parse_time(row.get('startTime'))
                end_time = self.parse_time(row.get('endTime'))
                created_time = self.parse_time(row.get('createdTime'))
                updated_time = self.parse_time(row.get('updatedTime'))

                task = CourseTask(
                    course_id=course_id,  # Directly assign the course_id
                    seq=self.parse_int(row.get('seq')),
                    activity_id=self.parse_int(row.get('activityId')),
                    title=row['title'],
                    is_free=bool(self.parse_int(row.get('isFree')) in [True, 1]),
                    is_optional=bool(self.parse_int(row.get('isOptional')) in [True, 1]),
                    start_time=start_time,
                    end_time=end_time,
                    status=row.get('status', 'unknown') if row.get('status') in dict(
                        CourseTask.STATUS_CHOICES).keys() else 'unknown',
                    created_user_id=self.parse_int(row.get('createdUserId')),
                    created_time=created_time,
                    updated_time=updated_time
                )

                tasks_to_create.append(task)
                if (i + 1) % 1000 == 0:
                    self.stdout.write(f"已处理 {i + 1} 行课程任务数据...")

        CourseTask.objects.bulk_create(tasks_to_create, batch_size=1000)
        self.stdout.write(f"成功导入 {len(tasks_to_create)} 条课程任务数据。跳过 {skipped_count} 条数据。")
