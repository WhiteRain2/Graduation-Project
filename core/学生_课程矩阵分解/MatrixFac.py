import torch
import numpy as np
import pandas as pd
from torch.autograd import Variable
import torch.nn.functional as F


class MatrixFactorization(torch.nn.Module):
    def __init__(self, n_users, n_items, n_factors=20):
        super(MatrixFactorization, self).__init__()
        self.user_factors = torch.nn.Embedding(n_users, n_factors, sparse=True)
        self.item_factors = torch.nn.Embedding(n_items, n_factors, sparse=True)

    def forward(self, user, item):
        return (self.user_factors(user) * self.item_factors(item)).sum(1)

    def predict(self, user, item):
        return self.forward(user, item)


# 添加函数以计算余弦相似度
def compute_cosine_similarity(matrix):
    # Normalize the matrix to compute cosine similarity
    norm_matrix = F.normalize(matrix)
    similarity = torch.mm(norm_matrix, norm_matrix.t())
    return similarity


if __name__ == '__main__':
    # 读取数据
    path = "D:/毕业设计/数据/DatasetOneResult/"
    df = pd.read_csv(f'{path}scores.csv')

    # 将userId和courseId映射到索引
    df['userId'], unique_users = pd.factorize(df['userId'])
    df['courseId'], unique_courses = pd.factorize(df['courseId'])

    # 计算用户数和课程数
    num_users = len(unique_users)
    num_courses = len(unique_courses)

    # 创建模型
    num_factors = 64  # 这里选择隐因子数量为64，可根据实际情况调整
    model = MatrixFactorization(num_users, num_courses, n_factors=num_factors)

    # 损失函数和优化器
    loss_fn = torch.nn.MSELoss()  # 均方误差损失
    optimizer = torch.optim.SparseAdam(model.parameters(), lr=1e-1)

    # 训练模型
    num_epochs = 10
    for epoch in range(num_epochs):
        for row in df.itertuples():
            user = Variable(torch.LongTensor([row.userId]))
            item = Variable(torch.LongTensor([row.courseId]))
            score = Variable(torch.FloatTensor([row.score]))

            # 预测
            prediction = model.predict(user, item)
            loss = loss_fn(prediction, score)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f'Epoch {epoch + 1}/{num_epochs} - Loss: {loss.data}')

    # 计算并保存学生相似度和课程相似度矩阵
    student_similarity = compute_cosine_similarity(model.user_factors.weight.data)
    course_similarity = compute_cosine_similarity(model.item_factors.weight.data)

    # 将相似度矩阵转换为NumPy数组并保存
    np.save('student_similarity.npy', student_similarity.numpy())
    np.save('course_similarity.npy', course_similarity.numpy())

    # 保存用户和课程的原始ID与新索引之间的映射关系
    # 正确保存 pd.factorize() 返回的唯一值数组，它们包含原始ID到新索引的映射
    np.save('user_ids_index_mapping.npy', unique_users)
    np.save('course_ids_index_mapping.npy', unique_courses)

    print('学生相似度和课程相似度矩阵以及映射关系已经保存。')