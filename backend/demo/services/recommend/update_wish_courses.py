from demo.models import Student, Course, WishCourse, Community, CourseSimilarity


def update_student_wish_courses(student, wish_course):
    if wish_course in student.wish_courses.all():
        return False
    if student.wish_courses.count() < Student.MAX_WISH_COURSES:
        # 将课程添加到学生的愿望课程中
        WishCourse.objects.create(student=student, course=wish_course)
    else:
        # 如果愿望课程已满，则替换最旧的愿望课程
        oldest_wish_course = student.wish_courses.order_by('wishcourse__timestamp').first()
        WishCourse.objects.filter(student=student, course=oldest_wish_course).delete()
        WishCourse.objects.create(student=student, course=wish_course)
    return True
