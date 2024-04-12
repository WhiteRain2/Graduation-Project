import pandas as pd

if __name__ == '__main__':
    # 读取数据
    path = "D:/毕业设计/数据/DatasetOneResult/"
    df = pd.read_csv(f'{path}scores.csv')

    # 计算学生总人数（假定ID连续，最大ID代表学生总数）
    total_students_estimate = df['userId'].max()

    # 计算实际选课的学生总人数
    total_students_with_courses = df['userId'].nunique()

    # 计算课程总数
    total_courses = df['courseId'].nunique()

    # 计算每位学生修了几门课，并找出修课程最多的数量
    courses_per_student = df.groupby('userId')['courseId'].count()
    max_courses_by_student = courses_per_student.max()

    # 使用差值计算未选课的学生数
    students_without_courses_estimate = total_students_estimate - total_students_with_courses

    # 输出所有信息
    print(f'Estimated total number of students based on userID: {total_students_estimate}')
    print(f'Total number of students with courses: {total_students_with_courses}')
    print(f'Total number of courses: {total_courses}')
    print(f'Most courses taken by a single student: {max_courses_by_student}')
    print(f'Estimated number of students without courses: {students_without_courses_estimate}')

    # 如果需要，也可以输出每名学生修了几门课的具体情况
    print(courses_per_student)