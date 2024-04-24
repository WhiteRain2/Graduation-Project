# views/getInformation/index.py

from django.http import JsonResponse


def get_student_list(student):
    # 获取已完成的课程
    completed_courses_json = [{'id': cc.course.course_id, 'name': cc.course.name, 'score': cc.score}
                              for cc in student.completedcourse_set.all()]

    # 获取愿望课程
    wish_courses_json = [{'id': wc.course.course_id, 'name': wc.course.name}
                         for wc in student.wishcourse_set.all()]

    # 获取已加入的共同体及其基本信息
    communities_json = [{'id': cm.id, 'name': cm.name, 'description': cm.description}
                        for cm in student.communities.all()]

    # 返回 JSON 响应
    return JsonResponse({
        'id': student.student_id,
        'name': student.name,
        'gender': student.get_gender_display(),
        'learning_style': student.get_learning_style_display(),
        'activity_level': student.activity_level,
        'self_description': student.self_description,
        'completed_courses': completed_courses_json,
        'wish_courses': wish_courses_json,
        'communities_count': len(communities_json),
        'communities': communities_json,
    })


def get_community_list(community):
    # 获取社区成员及其基本信息
    members_json = [{'id': student.student_id,
                     'name': student.name,
                     'gender': student.get_gender_display(),
                     'learning_style': student.get_learning_style_display(),
                     'self_description': student.self_description}
                    for student in community.members.all()]
    # 获取已完成的课程
    completed_courses_json = [{'id': cc.course.course_id, 'name': cc.course.name, 'member_ratio': cc.member_ratio}
                              for cc in community.completedcourse_set.all()]

    # 获取愿望课程
    wish_courses_json = [{'id': wc.course.course_id, 'name': wc.course.name, 'member_ratio': wc.member_ratio}
                         for wc in community.wishcourse_set.all()]

    # 返回 JSON 响应
    return JsonResponse({
        'id': community.id,
        'name': community.name,
        'description': community.description,
        'gender_ratio': community.gender_ratio,
        'learning_style': community.learning_style,
        'activity_level': community.activity_level,
        'members_count': community.members.count(),
        'members': members_json,
        'completed_courses': completed_courses_json,
        'wish_courses': wish_courses_json,
    })