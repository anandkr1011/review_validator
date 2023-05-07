from django.urls import path
from review_detector_api import views

urlpatterns = [
    path('',views.index),
    path('predict', views.detect_review),
]