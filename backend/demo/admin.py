# demo/admin.py
from django.contrib import admin
from django.urls import reverse
from .models.student import Student
from .models.community import Community
from .models.course import Course
from .models.relations import CommunityCompletedCourse, CommunityWishCourse, CompletedCourse, WishCourse
from .models.similarity import StudentSimilarity, CourseSimilarity
from .models.student_profile import StudentProfile
from .models.message import Message
from .models.homo_student_similarity import HomoStudentSimilarity
from django.utils.html import format_html

# demo/admin.py
# ...省略了其他导入...


# 自定义HomoStudentSimilarity模型的admin显示
class HomoStudentSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_student_id', 'get_similarity_vector')

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_similarity_vector(self, obj):
        return str(obj.similarity_vector)
    get_similarity_vector.short_description = 'Similarity Vector'


# 自定义StudentSimilarity模型的admin显示
class StudentSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_student_id', 'get_similarity_vector')

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_similarity_vector(self, obj):
        return str(obj.similarity_vector)
    get_similarity_vector.short_description = 'Similarity Vector'


# 自定义CourseSimilarity模型的admin显示
class CourseSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_course_id', 'get_similarity_vector')

    def get_course_id(self, obj):
        return obj.course.course_id
    get_course_id.short_description = 'Course ID'

    def get_similarity_vector(self, obj):
        return str(obj.similarity_vector)
    get_similarity_vector.short_description = 'Similarity Vector'


# 自定义学生模型的admin显示
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'gender', 'learning_style',
                    'activity_level', 'list_completed_courses', 'list_wish_courses')

    def list_completed_courses(self, obj):
        return ", ".join(str(course.course_id) for course in obj.completed_courses.all())
    list_completed_courses.short_description = 'Completed Courses IDs'

    def list_wish_courses(self, obj):
        return ", ".join(str(course.course_id) for course in obj.wish_courses.all())
    list_wish_courses.short_description = 'Wish Courses IDs'


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_student_id', 'get_name', 'get_user_id')

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_name(self, obj):
        if obj.student.name != obj.user.username:
            return f"{obj.user.username}_OOBS"
        return obj.student.name
    get_name.short_description = 'Name'

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = 'User ID'


# 自定义共同体模型的admin显示
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender_ratio', 'learning_style', 'activity_level',
                    'list_member_ids', 'list_completed_courses', 'list_wish_courses')

    def list_member_ids(self, obj):
        return ", ".join(str(member.student_id) for member in obj.members.all())
    list_member_ids.short_description = 'Members IDs'

    def list_completed_courses(self, obj):
        return ", ".join(str(course.course_id) for course in obj.completed_courses.all())
    list_completed_courses.short_description = 'Completed Courses IDs'

    def list_wish_courses(self, obj):
        return ", ".join(str(course.course_id) for course in obj.wish_courses.all())
    list_wish_courses.short_description = 'Wish Courses IDs'


# 自定义课程模型的admin显示
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'chapter_count', 'task_count', 'description')
    search_fields = ('name', 'description')
    list_filter = ('chapters__status', 'tasks__status')

    # 设定每页展示多少条目
    list_per_page = 25

    def get_queryset(self, request):
        # 优化查询，减少数据库访问
        queryset = super().get_queryset(request).prefetch_related('chapters', 'tasks')
        return queryset

    def chapter_count(self, obj):
        # 计算并展示章节数量
        return obj.chapters.count()

    chapter_count.short_description = '章节数量'  # 设置列的标题

    def task_count(self, obj):
        # 计算并展示任务数量
        return obj.tasks.count()

    task_count.short_description = '任务数量'  # 设置列的标题

    def view_course_detail(self, obj):
        # 提供一个查看详情的链接，可以根据实际需求设计跳转页面
        return format_html('<a href="{}">查看详情</a>', reverse('admin:app_course_change', args=[obj.pk]))

    view_course_detail.short_description = '课程详情'  # 设置列的标题


# 注册模型和其对应的自定义admin类
admin.site.register(Student, StudentAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(HomoStudentSimilarity, HomoStudentSimilarityAdmin)
admin.site.register(StudentSimilarity, StudentSimilarityAdmin)
admin.site.register(CourseSimilarity, CourseSimilarityAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)

# 针对关系模型保持默认的admin显示
admin.site.register(CommunityCompletedCourse)
admin.site.register(CommunityWishCourse)
admin.site.register(CompletedCourse)
admin.site.register(WishCourse)
admin.site.register(Message)
