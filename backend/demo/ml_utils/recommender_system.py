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
    def compute_cosine_similarity(matrix):
        norm_matrix = F.normalize(matrix)
        similarity = torch.mm(norm_matrix, norm_matrix.t())
        return similarity.numpy()

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
        # 计算基于学习成果的相似性
        student_similarity_matrix = RecommenderSystem.compute_cosine_similarity(model.user_factors.weight.data)
        course_similarity_matrix = RecommenderSystem.compute_cosine_similarity(model.item_factors.weight.data)

        # 直接更新学生相似性矩阵的值，而不创建个人相似性矩阵和融合矩阵
        for i, student1 in enumerate(self.students):
            for j, student2 in enumerate(self.students):
                if i != j:
                    # 计算基于个人信息的相似性
                    personal_similarity = RecommenderSystem.calculate_personal_similarity(student1, student2)
                    # 更新学生相似性矩阵的值
                    student_similarity_matrix[i][j] = (student_similarity_matrix[i][j] + personal_similarity) / 2

        return student_similarity_matrix, course_similarity_matrix

    def save_similarities(self, combined_student_similarity_matrix, course_similarity_matrix):
        with transaction.atomic():
            # Save student similarities
            for i, student in enumerate(self.students):
                similarities = combined_student_similarity_matrix[i]
                top_indices = similarities.argsort()[-self.top_n - 1:-1][::-1]
                top_scores = similarities[top_indices].tolist()
                original_student_ids = [self.students[idx].student_id for idx in top_indices]
                similarity_vector = dict(zip(original_student_ids, top_scores))
                StudentSimilarity.objects.update_or_create(student=student,
                                                           defaults={'similarity_vector': similarity_vector})

            # Save course similarities
            for i, course in enumerate(self.courses):
                similarities = course_similarity_matrix[i]
                top_indices = similarities.argsort()[-self.top_n - 1:-1][::-1]
                top_scores = similarities[top_indices].tolist()
                original_course_ids = [self.courses[idx].course_id for idx in top_indices]
                similarity_vector = dict(zip(original_course_ids, top_scores))
                CourseSimilarity.objects.update_or_create(course=course,
                                                          defaults={'similarity_vector': similarity_vector})

    def calculate(self):
        # Prepare data
        print('preparing data...')
        self.prepare_data()

        # Train the model
        print('training model...')
        model = self.train_model()

        # Compute similarity matrices
        print('computing similarity matrices...')
        combined_student_similarity_matrix, course_similarity_matrix = self.compute_similarity_matrices(model)

        # Save similarities to the database
        print('saving similarities...')
        self.save_similarities(combined_student_similarity_matrix, course_similarity_matrix)

        print(
            f'Top {self.top_n} student and course similarities have been saved to the database with original indices.')
