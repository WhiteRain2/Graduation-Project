import json
import torch
import torch.nn.functional as F
from django.db import transaction
from demo.models import Student, Course, StudentSimilarity, CourseSimilarity, CompletedCourse


class RecommenderSystem:
    def __init__(self, num_factors=64, num_epochs=10, top_n=10):
        self.num_factors = num_factors
        self.num_epochs = num_epochs
        self.top_n = top_n
        self.student_index_map = {}
        self.course_index_map = {}
        self.students = []
        self.courses = []
        self.completed_courses = []

    class MatrixFactorization(torch.nn.Module):
        def __init__(self, n_users, n_items, n_factors=20):
            super(RecommenderSystem.MatrixFactorization, self).__init__()
            self.user_factors = torch.nn.Embedding(n_users, n_factors, sparse=True)
            self.item_factors = torch.nn.Embedding(n_items, n_factors, sparse=True)

        def forward(self, user, item):
            return (self.user_factors(user) * self.item_factors(item)).sum(1)

    @staticmethod
    def calculate_personal_similarity(student1, student2):
        """计算两个学生间基于个人信息的相似度"""
        # 性别相似度：异质
        gender_similarity = 1 if student1.gender != student2.gender else 0

        # 学习风格相似度：异质
        learning_style_similarity = 1 if student1.learning_style != student2.learning_style else 0

        # 活跃度相似度：平均值接近0.5
        avg_activity_level = (student1.activity_level + student2.activity_level) / 2
        activity_similarity = 1 - abs(avg_activity_level - 0.5)  # 越接近0.5，相似度越高

        # 综合相似度平均计算
        total_similarity = (gender_similarity + learning_style_similarity + activity_similarity) / 3

        return total_similarity

    def compute_top_n_cosine_similarity(self, matrix, batch_size=500):
        # 规范化矩阵以获得单位长度的向量
        norm_matrix = F.normalize(matrix)
        n = norm_matrix.size(0)

        # 初始化最终结果矩阵
        top_indices = torch.empty((n, self.top_n), dtype=torch.long)
        top_values = torch.empty((n, self.top_n))

        # 处理matrix的每一个批次
        for idx in range(0, n, batch_size):
            # 计算当前批次的规范化矩阵与整个规范化矩阵的点积
            start_idx = idx
            end_idx = min(idx + batch_size, n)
            batch_matrix = norm_matrix[start_idx:end_idx]
            similarity_batch = torch.mm(batch_matrix, norm_matrix.t())

            # 计算Top N相似性，+1是因为每个向量与自己的相似度也包含在内
            top_values_batch, top_indices_batch = torch.topk(similarity_batch, self.top_n + 1, largest=True)

            # 除去每个向量与其自身的相似度
            top_indices_batch = top_indices_batch[:, 1:]
            top_values_batch = top_values_batch[:, 1:]

            # 把批处理结果存入最终结果矩阵
            top_indices[start_idx:end_idx] = top_indices_batch
            top_values[start_idx:end_idx] = top_values_batch

        # 数据从Torch tensor转换为NumPy数组
        return top_indices.numpy(), top_values.numpy()

    def prepare_data(self):
        self.students = list(Student.objects.all().order_by('student_id'))
        self.courses = list(Course.objects.all().order_by('course_id'))
        self.completed_courses = list(CompletedCourse.objects.all().select_related('student', 'course'))
        # Index mapping
        self.student_index_map = {student.student_id: index for index, student in enumerate(self.students)}
        self.course_index_map = {course.course_id: index for index, course in enumerate(self.courses)}

    def train_model(self):
        num_users = len(self.students)
        num_courses = len(self.courses)
        model = RecommenderSystem.MatrixFactorization(num_users, num_courses, n_factors=self.num_factors)
        loss_fn = torch.nn.MSELoss()
        optimizer = torch.optim.SparseAdam(model.parameters(), lr=1e-1)
        model.train()

        for epoch in range(self.num_epochs):
            for cc in self.completed_courses:
                user_index = self.student_index_map[cc.student.student_id]
                item_index = self.course_index_map[cc.course.course_id]
                user = torch.LongTensor([user_index])
                item = torch.LongTensor([item_index])
                score = torch.FloatTensor([cc.score])

                prediction = model(user, item)
                loss = loss_fn(prediction, score)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            print(f'Epoch {epoch + 1}/{self.num_epochs}, Loss: {loss.item()}')

        return model

    def compute_similarity_matrices(self, model):
        student_indices, student_similarities = self.compute_top_n_cosine_similarity(model.user_factors.weight.data)
        course_indices, course_similarities = self.compute_top_n_cosine_similarity(model.item_factors.weight.data)

        student_top_n_similarity_dict = {}
        course_top_n_similarity_dict = {}

        # 遍历学生，计算并更新其TOP N相似学生列表
        for i, student1 in enumerate(self.students):
            top_similar_students = []
            sim_indices = student_indices[i]
            sim_values = student_similarities[i]
            for idx, sim_value in zip(sim_indices, sim_values):
                student2 = self.students[idx]
                personal_similarity = RecommenderSystem.calculate_personal_similarity(student1, student2)
                combined_similarity = (sim_value + personal_similarity) / 2
                top_similar_students.append((student2, combined_similarity))  # 存储对象而不是ID
            top_similar_students = sorted(top_similar_students, key=lambda x: x[1], reverse=True)[:self.top_n]
            student_top_n_similarity_dict[student1] = top_similar_students  # 使用对象作为键

        # 遍历课程, 计算并更新TOP N课程列表
        for i, course1 in enumerate(self.courses):
            top_similar_courses = []
            sim_indices = course_indices[i]
            sim_values = course_similarities[i]
            for idx, sim_value in zip(sim_indices, sim_values):
                course2 = self.courses[idx]
                top_similar_courses.append((course2, sim_value))  # 存储对象而不是ID
            top_similar_courses = sorted(top_similar_courses, key=lambda x: x[1], reverse=True)[:self.top_n]
            course_top_n_similarity_dict[course1] = top_similar_courses  # 使用对象作为键

        return student_top_n_similarity_dict, course_top_n_similarity_dict

    def save_similarities(self, student_similarity_dict, course_similarity_dict):
        with transaction.atomic():
            StudentSimilarity.objects.all().delete()
            CourseSimilarity.objects.all().delete()

            student_similarity_list = []
            course_similarity_list = []

            # Prepare StudentSimilarity objects
            for student, students in student_similarity_dict.items():
                similarity_dict = {str(s.student_id): float(similarity) for s, similarity in students}
                student_similarity = StudentSimilarity(student=student, similarity_vector=json.dumps(similarity_dict))
                student_similarity_list.append(student_similarity)

            # Bulk create for StudentSimilarity
            StudentSimilarity.objects.bulk_create(student_similarity_list)

            # Prepare CourseSimilarity objects
            for course, courses in course_similarity_dict.items():
                similarity_dict = {str(c.course_id): float(similarity) for c, similarity in courses}
                course_similarity = CourseSimilarity(course=course, similarity_vector=json.dumps(similarity_dict))
                course_similarity_list.append(course_similarity)

            # Bulk create for CourseSimilarity
            CourseSimilarity.objects.bulk_create(course_similarity_list)

    def calculate(self):
        # Prepare data
        print('preparing data...')
        self.prepare_data()

        # Train the model
        print('training model...')
        model = self.train_model()

        # Compute similarity matrices
        print('computing similarity matrices...')
        student_similarity_dict, course_similarity_dict = self.compute_similarity_matrices(model)

        # Save similarities to the database
        print('saving similarities...')
        self.save_similarities(student_similarity_dict, course_similarity_dict)

        print(
            f'Top {self.top_n} student and course similarities have been saved to the database with original indices.')
