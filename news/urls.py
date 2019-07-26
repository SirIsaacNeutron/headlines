from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='news-home'),
    path('results/', views.results, name='news-results'),
    path('<str:category>/', views.category, name='news-category'),
]
