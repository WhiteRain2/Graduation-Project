import torch
from torch.autograd import Variable
import torch.nn.functional as F
from demo.models import Student, Course, StudentSimilarity, CourseSimilarity, CompletedCourse
from django.db import transaction


class MatrixFactorization(torch.nn.Module):
    def __init__(self, n_users, n_items, n_factors=20):
        super(MatrixFactorization, self).__init__()
        self.user_factors = torch.nn.Embedding(n_users, n_factors, sparse=True)
        self.item_factors = torch.nn.Embedding(n_items, n_factors, sparse=True)

    def forward(self, user, item):
        return (self.user_factors(user) * self.item_factors(item)).sum(1)

    def predict(self, user, item):
        return self.forward(user, item)


def compute_cosine_similarity(matrix):
    # Normalize the matrix to compute cosine similarity
    norm_matrix = F.normalize(matrix)
    similarity = torch.mm(norm_matrix, norm_matrix.t())
    return similarity


def calculate_and_save_similarities(num_factors=64, num_epochs=10, top_n=10):
    # 获取学生和课程的完整列表
    students = Student.objects.all().order_by('student_id')
    courses = Course.objects.all().order_by('course_id')

    num_users = students.count()
    num_courses = courses.count()

    # 映射学生ID到模型内部用户索引
    student_index_map = {student.student_id: index for index, student in enumerate(students)}
    # 映射课程ID到模型内部项目索引
    course_index_map = {course.course_id: index for index, course in enumerate(courses)}

    # 创建模型
    model = MatrixFactorization(num_users, num_courses, n_factors=num_factors)

    # 损失函数和优化器
    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.SparseAdam(model.parameters(), lr=1e-1)
    model.train()

    # 训练模型
    for epoch in range(num_epochs):
        for cc in CompletedCourse.objects.all().select_related('student', 'course'):
            user_index = student_index_map[cc.student.student_id]
            item_index = course_index_map[cc.course.course_id]
            user = Variable(torch.LongTensor([user_index]))
            item = Variable(torch.LongTensor([item_index]))
            score = Variable(torch.FloatTensor([cc.score]))

            # 预测和损失计算
            prediction = model(user, item)
            loss = loss_fn(prediction, score)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}')

    # 计算学生和课程的相似度矩阵
    student_similarity_matrix = compute_cosine_similarity(model.user_factors.weight.data).cpu().numpy()
    course_similarity_matrix = compute_cosine_similarity(model.item_factors.weight.data).cpu().numpy()

    # 保存学生相似度到数据库
    with transaction.atomic():
        for i, student in enumerate(students):
            # 取出与当前学生最相似的TOP N学生的索引和相似分数
            similarities = student_similarity_matrix[i]
            top_indices = similarities.argsort()[-top_n - 1:-1][::-1]  # 跳过自身，然后取TOP N
            top_scores = similarities[top_indices].tolist()
            # 将模型内部索引转换为原始student_id
            original_student_ids = [list(student_index_map.keys())[list(student_index_map.values()).index(idx)] for idx
                                    in top_indices]
            # 构造相似度向量为JSON格式，使用原始student_id作为key
            similarity_vector = dict(zip(original_student_ids, top_scores))
            # 更新或创建记录
            StudentSimilarity.objects.update_or_create(
                student=student,
                defaults={'similarity_vector': similarity_vector}
            )

    # 保存课程相似度到数据库
    with transaction.atomic():
        for i, course in enumerate(courses):
            # 取出与当前课程最相似的TOP N课程的索引和相似分数
            similarities = course_similarity_matrix[i]
            top_indices = similarities.argsort()[-top_n - 1:-1][::-1]  # 跳过自身，然后取TOP N
            top_scores = similarities[top_indices].tolist()
            # 将模型内部索引转换为原始course_id
            original_course_ids = [list(course_index_map.keys())[list(course_index_map.values()).index(idx)] for idx in
                                   top_indices]
            # 构造相似度向量为JSON格式，使用原始course_id作为key
            similarity_vector = dict(zip(original_course_ids, top_scores))
            # 更新或创建记录
            CourseSimilarity.objects.update_or_create(
                course=course,
                defaults={'similarity_vector': similarity_vector}
            )

    print(f'Top {top_n} student and course similarities have been saved to the database with original indices.')
