# demo/tasks.py
from celery import shared_task
from .ml_utils.calculation import calculate_and_save_similarities


@shared_task
def calculate_similarities_task():
    calculate_and_save_similarities(num_factors=64, num_epochs=10, top_n=10)
