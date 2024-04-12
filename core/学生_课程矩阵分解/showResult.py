import numpy as np
import matplotlib.pyplot as plt


def load_and_inspect_similarity_matrix(file_path):
    # 加载相似度矩阵
    similarity = np.load(file_path)
    print(f"Loaded similarity matrix from {file_path} with shape: {similarity.shape}")

    # 展示相似度矩阵的基础信息
    print(f'Minimum similarity: {np.min(similarity)}')
    print(f'Maximum similarity: {np.max(similarity)}')
    print(f'Average similarity: {np.mean(similarity)}')

    # 可视化展示矩阵的热图
    # plt.figure(figsize=(10, 8))
    # plt.title(f"Heatmap of similarity matrix: {file_path}")
    # plt.imshow(similarity, cmap='hot', interpolation='nearest')
    # plt.colorbar()
    # plt.show()


if __name__ == '__main__':
    # 调用函数查看学生相似度矩阵
    load_and_inspect_similarity_matrix('student_similarity.npy')

    # 调用函数查看课程相似度矩阵
    load_and_inspect_similarity_matrix('course_similarity.npy')