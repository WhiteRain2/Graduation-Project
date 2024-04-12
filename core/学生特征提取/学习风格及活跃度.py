import pandas as pd
import json
from tqdm import tqdm

# 辅助函数：解析JSON格式的学习行为数据
def parse_json_data(json_str):
    try:
        return json.loads(json_str.replace("'", "\""))
    except json.JSONDecodeError:
        return {}


# 辅助函数：计算观看视频总时长
def calculate_total_watch_time(user_activities):
    total_time = 0
    for activity_data in user_activities:
        if activity_data.get('event') == 'watching':
            total_time += int(activity_data.get('watchTime', 0))
    return total_time


# 判定学生学习风格的函数
def determine_learning_style(row):
    # 判断逻辑同之前
    total_watch_time = row['TotalWatchTime']
    total_learned_time = row['TotalLearnedTime']
    # 使用特定的规则判定学习风格
    if row['joinedClassroomNum'] + row['joinedCourseSetNum'] > 5 and total_watch_time > total_learned_time:
        return '发散型'
    elif row['learnedSeconds'] > 10 * 60 * 60:
        return '同化型'
    elif row['finishedTaskNum'] > 10 and row['learnedSeconds'] > 5 * 60 * 60:
        return '聚敛型'
    elif row['joinedClassroomNum'] > 3 and row['learnedSeconds'] < 5 * 60 * 60:
        return '顺应型'
    else:
        return '未知'


# 计算活跃度的函数
def calculate_activity_level(row, user_activity_counts, user_media_type_diversity):
    user_id = row.name  # 因为index是userId
    user_stats = row.to_dict()
    user_activities = user_activity_counts.get(user_id, 0)
    user_media_diversity = len(user_media_type_diversity.get(user_id, set()))

    # 基于不同的指标计算总的活跃度得分
    activity_level = (
            user_stats['learnedSeconds'] * 0.3 +
            user_stats['finishedTaskNum'] * 0.3 +
            (user_stats['joinedClassroomNum'] + user_stats['joinedCourseSetNum'] + user_stats[
                'joinedCourseNum']) * 0.1 +
            user_activities * 0.2 +
            user_media_diversity * 0.1
    )
    return activity_level


if __name__ == '__main__':
    # 设置数据文件的路径
    path = "D:/毕业设计/数据/DatasetOne/"
    outPath = "D:/毕业设计/数据/DatasetOneResult/"

    # 加载学习统计数据
    df_learn_statistics = pd.read_csv(f'{path}user_learn_statistics_total.csv', index_col='userId')

    # 初始化学习风格和活跃度列
    df_combined = df_learn_statistics.copy()
    df_combined['LearningStyle'] = '未知'
    df_combined['ActivityLevel'] = 0
    df_combined['TotalWatchTime'] = 0  # 新增列，用于存储总观看时间
    df_combined['TotalLearnedTime'] = 0  # 新增列，用于存储总学习时间

    # 初始化用户活动计数和媒体类型多样性
    user_activity_counts = {}
    user_media_type_diversity = {}

    # 分块处理活动日志数据文件
    chunk_size = 50000  # 根据实际内存调整
    progress_bar = tqdm(pd.read_csv(f'{path}activity_learn_log.csv', chunksize=chunk_size))  # 使用tqdm创建进度条
    for chunk in progress_bar:
        chunk['data'] = chunk['data'].apply(parse_json_data)  # 转换 data 字段为字典

        # 累加每个用户的观看时间和学习时间
        for idx, row in chunk.iterrows():
            try:
                user_id = row['userId']
                activity_data = row['data']  # 这里直接使用已经转换为字典的数据

                if user_id not in user_activity_counts:
                    user_activity_counts[user_id] = 0
                    user_media_type_diversity[user_id] = set()

                user_activity_counts[user_id] += 1
                user_media_type_diversity[user_id].add(activity_data.get('mediaType'))

                df_combined.at[user_id, 'TotalWatchTime'] += calculate_total_watch_time([activity_data])
                df_combined.at[user_id, 'TotalLearnedTime'] += row['learnedTime']
            except:
                print("error")

    # 应用判定学生学习风格和活跃度的函数
    df_combined['LearningStyle'] = df_combined.apply(determine_learning_style, axis=1)
    df_combined['ActivityLevel'] = df_combined.apply(calculate_activity_level, axis=1,
                                                     args=(user_activity_counts, user_media_type_diversity))

    # 保存结果到CSV文件，仅包含userId, LearningStyle和ActivityLevel
    df_combined = df_combined[['LearningStyle', 'ActivityLevel']]
    df_combined.to_csv(f'{outPath}students_activity_and_styles.csv', index_label='userId')

    progress_bar.close()
