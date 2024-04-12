class StudyCommunity:
    def __init__(self, comId, member_ids, completed_courses, wish_courses,
                 calculate_course_similarity, calculate_member_similarity,
                 MAX_MEMBERS=8, MAX_WISH_COURSES=5):
        """
        构造学习共同体类。

        :param comId: int, 共同体的唯一标识符
        :param member_ids: list, 成员的id列表
        :param completed_courses: list, 包含成员已完成课程id和成绩的列表
        :param wish_courses: list, 包含成员想学的课程id列表（0-MAX_WISH_COURSES个）
        :param calculate_course_similarity: function, 计算课程相似度的函数
        :param calculate_member_similarity: function, 计算成员相似度的函数
        :param MAX_MEMBERS: int, 共同体最大成员数
        :param MAX_WISH_COURSES: int, 最大愿望课程列表长度
        """
        self.comId = comId
        self.member_ids = member_ids
        self.completed_courses = completed_courses
        self.wish_courses = wish_courses
        self.calculate_course_similarity = calculate_course_similarity
        self.calculate_member_similarity = calculate_member_similarity
        self.MAX_MEMBERS = MAX_MEMBERS
        self.MAX_WISH_COURSES = MAX_WISH_COURSES
        self.member_count = len(member_ids)

    def join_member(self, new_member_id, new_member_completed_courses, new_member_wish_courses):
        """
        学生选择加入共同体，并按照规则更新共同体的已修课程和愿望课程列表。

        :param new_member_id: int, 新成员的id
        :param new_member_completed_courses: list, 新成员已修课程列表
        :param new_member_wish_courses: list, 新成员的愿望课程列表
        :return: bool, 新成员是否成功加入
        """
        if self.member_count >= self.MAX_MEMBERS or new_member_id in self.member_ids:
            return False  # 超过最大成员数或已在其中，加入失败

        # Set operation for updating completed_courses and wish_courses
        completed_courses_set = set([course['id'] for course in self.completed_courses])
        wish_courses_set = set(self.wish_courses)
        new_member_completed_courses_set = set([course['id'] for course in new_member_completed_courses])
        new_member_wish_courses_set = set(new_member_wish_courses)

        # Update the wish_courses by removing courses already known by the new member
        # and adding new wish courses from the new member
        # that were not known by the community before.
        updated_wish_courses = list((wish_courses_set - new_member_completed_courses_set) |
                                    (new_member_wish_courses_set - completed_courses_set))

        # Apply the max wish courses constraint
        self.wish_courses = updated_wish_courses[:self.MAX_WISH_COURSES]

        # Update the completed_courses by union with the new member's completed_courses
        self.completed_courses += [course for course in new_member_completed_courses
                                   if course['id'] not in completed_courses_set]

        # Add the new member
        self.member_ids.append(new_member_id)
        self.member_count += 1

        return True  # 成员成功加入

    def remove_member(self, member_id):
        """
        从共同体中移除一个学生成员，并更新团队已修课程列表。

        :param member_id: int, 要移除的成员的id
        :return: bool, 成员是否成功被移除
        """
        if member_id not in self.member_ids:
            return False  # 如果成员不在共同体中，移除失败

        # 首先，找出需要被移除的成员的已修课程列表
        member_courses_to_remove = [course for course in self.completed_courses if course['member_id'] == member_id]

        # 从共同体的成员ID列表中移除该成员
        self.member_ids.remove(member_id)
        self.member_count -= 1

        # 更新共同体的已学课程列表
        # 只保留那些不是被移除的学生独有的已修课程
        member_courses_to_remove_ids = set([course['id'] for course in member_courses_to_remove])
        self.completed_courses = [
            course for course in self.completed_courses
            if course['id'] not in member_courses_to_remove_ids or course['member_id'] != member_id
        ]

        return True  # 成员成功被移除

    def is_member_in_community(self, student_id):
        """
        判断指定学生是否属于这个共同体。

        :param student_id: int, 学生的ID
        :return: bool, 指定学生是否是共同体的成员
        """
        return student_id in self.member_ids

    def evaluate_member_similarity(self, student):
        """
        基于学生的愿望课程及已完成课程与共同体完成的课程和愿望课程列表相匹配的程度，计算学生与共同体的相似度。

        :param student: Student, 学生对象
        :return: float, 学生对象与共同体的相似度评分
        """
        # 计算学生愿望课程与共同体已完成课程的相似度评分
        wish_course_similarity = 0
        if student.wish_course and self.completed_courses:
            for completed_course in self.completed_courses:
                wish_course_similarity += self.calculate_course_similarity(student.wish_course, completed_course['id'])
            wish_course_similarity /= len(self.completed_courses)

        # 计算学生已完成课程与共同体愿望课程列表的相似度评分
        completed_course_similarity = 0
        if student.completed_courses and self.wish_courses:
            for student_completed_course in student.completed_courses:
                for wish_course_id in self.wish_courses:
                    completed_course_similarity += self.calculate_course_similarity(student_completed_course['id'],
                                                                                    wish_course_id)
            completed_course_similarity /= (len(student.completed_courses) * len(self.wish_courses))

        # 最终相似度评分是两部分匹配度的加权平均
        final_similarity_score = 0.5 * wish_course_similarity + 0.5 * completed_course_similarity

        return final_similarity_score

    def calculate_avg_course_similarity(self):
        """
        计算学习共同体中所有已修课程之间的平均相似度。

        :return: float, 所有课程对之间相似度的平均值
        """
        # 确保共同体中有足够的课程进行相似度计算，至少需要2门不同课程
        if len(self.completed_courses) < 2:
            return 0.0  # 如果不足两门课程，则返回0

        # 初始化相似度总和和比较次数
        similarity_sum = 0
        comparisons = 0

        # 对共同体中已修课程两两之间进行相似度计算
        for i in range(len(self.completed_courses) - 1):
            for j in range(i + 1, len(self.completed_courses)):
                # 使用提供的课程相似度计算函数计算两门课程之间的相似度
                similarity = self.calculate_course_similarity(self.completed_courses[i], self.completed_courses[j])
                similarity_sum += similarity
                comparisons += 1

        # 计算平均相似度
        if comparisons == 0:  # 如果不存在可比较的课程对，返回0
            return 0.0
        else:
            return similarity_sum / comparisons

    def calculate_avg_member_similarity(self):
        """
        计算学习共同体中所有成员之间的平均相似度。

        :return: float, 所有成员对之间相似度的平均值
        """
        # 确保共同体中有足够的成员进行相似度计算，至少需要2个成员
        if len(self.member_ids) < 2:
            return 0.0  # 如果不足两个成员，则返回0

        # 初始化相似度总和和比较次数
        similarity_sum = 0
        comparisons = 0

        # 对共同体中成员两两之间进行相似度计算
        for i in range(len(self.member_ids) - 1):
            for j in range(i + 1, len(self.member_ids)):
                # 使用提供的成员相似度计算函数计算两个成员之间的相似度
                similarity = self.calculate_member_similarity(self.member_ids[i], self.member_ids[j])
                similarity_sum += similarity
                comparisons += 1

        # 计算平均相似度
        if comparisons == 0:  # 如果不存在可比较的成员对，返回0
            return 0.0
        else:
            return similarity_sum / comparisons
