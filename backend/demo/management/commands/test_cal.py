import torch
import random
from django.core.management.base import BaseCommand
from demo.models.student import Student
from demo.models.community import Community
from demo.views.recommend.community_recommender import CommunityRecommender


class Command(BaseCommand):
    help = 'Evaluate Recommendation System using PyTorch'

    def calculate_precision_recall_f1(self, y_true, y_pred):
        y_true = torch.tensor(y_true)
        y_pred = torch.tensor(y_pred)

        true_positives = (y_true * y_pred).sum().item()
        precision = true_positives / y_pred.sum().item() if y_pred.sum().item() > 0 else 0
        recall = true_positives / y_true.sum().item() if y_true.sum().item() > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return precision, recall, f1

    def calculate_map(self, y_true, y_pred):
        y_true = torch.tensor(y_true)
        y_pred = torch.tensor(y_pred)

        ap_sum = 0
        for i in range(y_true.size(0)):
            relevant = y_true[i].sum().item()
            if relevant == 0:
                continue
            correct = 0
            avg_precision = 0
            for j in range(y_true.size(1)):
                if y_true[i, j] == 1:
                    correct += 1
                    avg_precision += correct / (j + 1)
            avg_precision /= relevant
            ap_sum += avg_precision

        map_score = ap_sum / y_true.size(0)
        return map_score

    def calculate_ndcg(self, y_true, y_pred, k=10):
        y_true = torch.tensor(y_true).float()
        y_pred = torch.tensor(y_pred).float()

        sorted_indices = torch.argsort(y_pred, dim=1, descending=True)
        sorted_true = torch.gather(y_true, 1, sorted_indices)

        # Expand range to match the sorted_true tensor shape
        discount = torch.log2(torch.arange(2, k + 2).float())
        discount_expanded = discount.unsqueeze(0).expand(sorted_true.size(0),
                                                         -1)  # Expand it to have the same number of rows as sorted_true

        gains = (2 ** sorted_true - 1) / discount_expanded
        dcg = gains[:, :k].sum(1).mean().item()

        # Create ideal ranking order
        ideal_sorted_true = torch.sort(y_true, dim=1, descending=True)[0]
        ideal_gains = (2 ** ideal_sorted_true - 1) / discount_expanded
        idcg = ideal_gains[:, :k].sum(1).mean().item()

        ndcg_score = dcg / idcg if idcg > 0 else 0
        return ndcg_score

    def handle(self, *args, **options):
        y_true = []
        y_pred = []

        for student in Student.objects.all()[:500]:
            actual_communities = list(student.communities.values_list('id', flat=True))
            wish_courses = list(student.wish_courses.values_list('course_id', flat=True))
            if len(wish_courses) == 0:
                continue
            recommender = CommunityRecommender(student.student_id, random.choice(wish_courses))
            recommended_communities = recommender.recommend_communities()

            recommended_communities_ids = [community.id for _, community in recommended_communities]

            y_true_student = [1 if community.id in actual_communities else 0 for community in Community.objects.all()]
            y_pred_student = [1 if community.id in recommended_communities_ids else 0 for community in
                              Community.objects.all()]

            y_true.append(y_true_student)
            y_pred.append(y_pred_student)

        precision, recall, f1 = self.calculate_precision_recall_f1(y_true, y_pred)
        map_score = self.calculate_map(y_true, y_pred)
        ndcg = self.calculate_ndcg(y_true, y_pred)

        self.stdout.write(self.style.SUCCESS(f'Precision: {precision:.4f}'))
        self.stdout.write(self.style.SUCCESS(f'Recall: {recall:.4f}'))
        self.stdout.write(self.style.SUCCESS(f'F1-Score: {f1:.4f}'))
        self.stdout.write(self.style.SUCCESS(f'MAP: {map_score:.4f}'))
        self.stdout.write(self.style.SUCCESS(f'NDCG: {ndcg:.4f}'))
