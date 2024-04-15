from demo.repositories.community_repository import CommunityRepository
from demo.repositories.student_repository import StudentRepository


def student_join_community(student_id, community_id, MAX_COMMUNITIES=5):
    # 调用 StudentRepository 中定义的 join_community 方法
    StudentRepository.join_community(student_id, community_id, MAX_COMMUNITIES)


def student_leave_community(student_id, community_id):
    # 调用 CommunityRepository 中定义的 remove_member_from_community 方法
    CommunityRepository.remove_member_from_community(community_id, student_id)