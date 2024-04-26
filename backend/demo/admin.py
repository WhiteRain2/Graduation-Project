# demo/admin.py
from django.contrib import admin
from .models.student import Student
from .models.community import Community
from .models.course import Course
from .models.relations import CommunityCompletedCourse, CommunityWishCourse, CompletedCourse, WishCourse
from .models.similarity import StudentSimilarity, CourseSimilarity
from .models.student_profile import StudentProfile
from .models.message import Message
from .models.homo_student_similarity import HomoStudentSimilarity


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
    list_display = ('course_id', 'name', 'description')


# 注册模型和其对应的自定义admin类
admin.site.register(Student, StudentAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(HomoStudentSimilarity, HomoStudentSimilarityAdmin)
admin.site.register(StudentSimilarity, StudentSimilarityAdmin)
admin.site.register(CourseSimilarity, CourseSimilarityAdmin)

# 针对关系模型保持默认的admin显示
admin.site.register(CommunityCompletedCourse)
admin.site.register(CommunityWishCourse)
admin.site.register(CompletedCourse)
admin.site.register(WishCourse)
admin.site.register(StudentProfile)
admin.site.register(Message)