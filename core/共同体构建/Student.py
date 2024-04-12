class Student:
    def __init__(self, sId, communities, completed_courses, wish_courses, MAX_WISH_COURSES=5):
        """
        构造学生类。

        :param sId: int, 学生的唯一标识符
        :param communities: set, 学生当前参与的学习共同体集合
        :param completed_courses: list, 学生已经完成的课程列表，课程信息包括课程id和对应成绩
        :param wish_courses: list, 学生希望学习的课程id列表
        :param MAX_WISH_COURSES: int, 学生愿望课程列表的最大长度，默认为5
        """
        self.sId = sId
        self.communities = communities
        self.completed_courses = completed_courses
        self.wish_courses = wish_courses[:MAX_WISH_COURSES]  # 在初始化时就确保不超过最大愿望课程数量
        self.wish_course = None if not wish_courses else wish_courses[0]  # 初始化时设定的愿望课程
        self.MAX_WISH_COURSES = MAX_WISH_COURSES

    def add_completed_course(self, course_id, score):
        """
        向学生的已修课程列表中添加新课程。

        :param course_id: int, 要添加的新课程的id
        :param score: int, 学生在该课程中获得的成绩
        """
        # 检查课程是否已存在于已修课程列表中
        for course in self.completed_courses:
            if course['id'] == course_id:
                # 如果课程已存在，可以选择更新成绩，或者直接返回
                course['score'] = score
                return
        # 如果课程不存在，则添加到列表中
        self.completed_courses.append({'id': course_id, 'score': score})

    def remove_completed_course(self, course_id):
        """
        从学生的已修课程列表中移除课程。

        :param course_id: int, 要移除的课程的id
        """
        self.completed_courses = [course for course in self.completed_courses if course['id'] != course_id]

    def update_wish_course(self, course_id):
        """
        更新学生的当前愿望课程，并在必要时更新愿望课程列表。

        :param course_id: int, 学生希望学习的新课程的id
        """
        self.wish_course = course_id  # 设置当前的愿望课程
        if course_id not in self.wish_courses:
            # 如果愿望课程列表满了，则移除最早添加的课程，使用pop(0)
            if len(self.wish_courses) >= self.MAX_WISH_COURSES:
                self.wish_courses.pop(0)
            self.wish_courses.append(course_id)  # 添加新的愿望课程到列表

    def join_community(self, community):
        """
        学生加入学习共同体。

        :param community: StudyCommunity, 学生希望加入的学习共同体对象
        :return: bool, 学生是否成功加入共同体
        """
        if community.join_member(self):
            self.communities.add(community)
            return True
        else:
            return False

    def quit_community(self, community):
        """
        学生退出学习共同体。

        :param community: StudyCommunity, 学生希望退出的学习共同体对象
        :return: bool, 学生是否成功退出共同体
        """
        if community in self.communities and community.remove_member(self.sId):
            self.communities.remove(community)
            return True
        else:
            return False
