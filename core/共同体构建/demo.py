from Student import Student
from StudyCommunity import StudyCommunity
import pandas as pd
import numpy as np


# 更新的课程相似度计算函数
def calculate_course_similarity(course_a_id, course_b_id):
    # 加载相似度矩阵及索引关系
    course_id_to_index = {id_: index for index, id_ in enumerate(unique_courses)}

    # 通过原始ID获取索引
    course_a_index = course_id_to_index.get(course_a_id)
    course_b_index = course_id_to_index.get(course_b_id)

    # 检查两个课程ID是否都在映射字典中
    if course_a_index is not None and course_b_index is not None:
        # 使用索引获取相似度矩阵中的值
        return course_similarity_matrix[course_a_index, course_b_index]
    else:
        # 如果课程ID不在映射字典中，抛出异常提示
        raise ValueError(f"至少一个课程ID未找到: {course_a_id} 或 {course_b_id}")


def calculate_member_similarity(member_a_id, member_b_id):
    # 加载相似度矩阵及索引关系
    user_id_to_index = {id_: index for index, id_ in enumerate(unique_users)}

    # 通过原始ID获取索引
    member_a_index = user_id_to_index.get(member_a_id)
    member_b_index = user_id_to_index.get(member_b_id)

    # 检查两个用户ID是否都在映射字典中
    if member_a_index is not None and member_b_index is not None:
        # 使用索引获取相似度矩阵中的值
        return student_similarity_matrix[member_a_index, member_b_index]
    else:
        # 如果用户ID不在映射字典中，抛出异常提示
        raise ValueError(f"至少一个用户ID未找到: {member_a_id} 或 {member_b_id}")


def init(scores_df):
    students = {}
    communities = {}

    # 用于记录用户和其对应的共同体id
    student_to_community = {}

    # 用于为共同体分配独立的索引值
    next_community_id = 0

    scores_df['userId'] = scores_df['userId'].astype(int)
    scores_df['courseId'] = scores_df['courseId'].astype(int)

    for index, row in scores_df.iterrows():
        user_id = int(row['userId'])
        course_id = int(row['courseId'])
        score = row['score']

        # 创建或更新学生对象
        if user_id not in students:
            # 初始化学生对象
            students[user_id] = Student(sId=user_id,
                                        communities=set(),
                                        completed_courses=[{'id': course_id, 'score': score}],
                                        wish_courses=[],
                                        MAX_WISH_COURSES=5)

            # 初始化对应的共同体对象
            communities[next_community_id] = StudyCommunity(comId=next_community_id,
                                                            member_ids=[user_id],
                                                            completed_courses=[{'id': course_id, 'score': score}],
                                                            wish_courses=[],
                                                            calculate_course_similarity=calculate_course_similarity,
                                                            calculate_member_similarity=calculate_member_similarity,
                                                            MAX_MEMBERS=8,
                                                            MAX_WISH_COURSES=5)
            student_to_community[user_id] = next_community_id
            next_community_id += 1
        else:
            # 学生已存在，添加完成的课程
            students[user_id].add_completed_course(course_id, score)

            # 获取学生对应的共同体id，并更新该共同体的已完成的课程列表
            community_id = student_to_community[user_id]
            communities[community_id].completed_courses.append({'id': course_id, 'score': score})

    return students, communities


def recommend(student, wish_course, count=10):
    if wish_course in student.completed_courses:
        return False
    student.update_wish_course(wish_course)

    recommend_communities = []
    for community in communities.values():
        if community.member_count >= community.MAX_MEMBERS or community.is_member_in_community(student.sId):
            continue
        sim = community.evaluate_member_similarity(student)
        recommend_communities.append([sim, community])
    recommend_communities = sorted(recommend_communities, key=lambda x: x[0], reverse=True)
    return recommend_communities[:count]


def student_join_community(student, community):
    if community.member_count >= community.MAX_MEMBERS or community.is_member_in_community(student.sId):
        return False
    return student.join_community(community)


def study_quit_community(student, community):
    if not community.is_member_in_community(student.sId):
        return False
    return student.quit_community(community)


if __name__ == '__main__':
    # 读取CSV文件
    path = "D:/毕业设计/数据/DatasetOneResult/"
    scores_df = pd.read_csv(f'{path}scores.csv')

    unique_courses = np.load('../学生_课程矩阵分解/course_ids_index_mapping.npy')
    course_similarity_matrix = np.load('../学生_课程矩阵分解/course_similarity.npy')
    unique_users = np.load('../学生_课程矩阵分解/user_ids_index_mapping.npy')
    student_similarity_matrix = np.load('../学生_课程矩阵分解/student_similarity.npy')

    students, communities = init(scores_df)

    recommend_communities = recommend(students[3], 599)
    print(recommend_communities)

