# demo/tasks.py
from celery import shared_task
from .ml_utils.recommender_system import RecommenderSystem
import logging


@shared_task
def calculate_similarities_task():
    recommender = RecommenderSystem(num_factors=64, num_epochs=10, top_n=10)
    recommender.calculate()
