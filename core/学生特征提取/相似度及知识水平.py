# 数据集中存在的课程总数: 9424
# 数据集中的学生总数: 79917
import pandas as pd

path = "D:/毕业设计/数据/DatasetOne/"  # 您的数据文件夹路径
outPath = "D:/毕业设计/数据/DatasetOneResult"

# 加载数据
df_classroom_courses = pd.read_csv(f'{path}classroom_courses.csv')
df_testpaper_result = pd.read_csv(f'{path}testpaper_result.csv', low_memory=False)

# 仅保留classroom_courses表中courseId和其对应的班级ID
df_courses = df_classroom_courses[['courseId']].drop_duplicates()

# 根据课程ID合并classroom_courses与testpaper_result
df_merged = pd.merge(df_testpaper_result[['userId', 'courseId', 'lessonId', 'score']], df_courses, on='courseId')

# 排除得分为0的情况
df_merged = df_merged[df_merged['score'] != 0]

# 对每位学生的每个课程按课时ID分组，然后计算平均得分作为该课程的得分
df_course_avg_score = df_merged.groupby(['userId', 'courseId'])['score'].mean().reset_index()

# 将学生ID、课程ID、平均分保存到CSV文件
df_course_avg_score.to_csv(f'{outPath}student_course_total_scores.csv', index=False)

# 统计每位学生学过的课程数量
df_student_courses_count = df_course_avg_score.groupby('userId')['courseId'].count().reset_index(name='course_count')

# 统计每位学生60分以下的平均课程数量
df_student_fail_count = df_course_avg_score[df_course_avg_score['score'] < 60].groupby('userId')['courseId'].count().reset_index(name='fail_count')

# 统计每位学生所有课程的平均分数
df_student_avg_score = df_course_avg_score.groupby('userId')['score'].mean().reset_index(name='average_score')

# 统计每位学生得分为0的课程数量
# 注意：由于我们之前已经排除了所有0分的得分，这里我们需要重新从未经过滤的数据df_testpaper_result中进行统计
df_zero_score_count = df_testpaper_result[df_testpaper_result['score'] == 0].groupby('userId')['courseId'].count().reset_index(name='zero_score_count')

# 合并上述得到的统计数据
df_students_summary = pd.merge(df_student_courses_count, df_student_fail_count, on='userId', how='left')
df_students_summary = pd.merge(df_students_summary, df_student_avg_score, on='userId', how='left')
df_students_summary = pd.merge(df_students_summary, df_zero_score_count, on='userId', how='left')

# 对于没有不及格课程的情况，将NaN替换为0
df_students_summary['fail_count'].fillna(0, inplace=True)
df_students_summary['zero_score_count'].fillna(0, inplace=True) # 将NaN替换为0

# 保存这些统计数据到新的CSV文件
df_students_summary.to_csv(f'{outPath}students_statistics_summary.csv', index=False)

print(df_students_summary.head())  # 打印前几行数据以检查结果