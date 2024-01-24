from django.urls import path
from . import views

urlpatterns = [
    path('webSearch/', views.main_page, name='webSearch'),
    path('', views.main_page, name='webSearch'),
]