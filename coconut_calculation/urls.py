from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer-list'),
    path('customers/<str:mobile_number>/', views.customer_detail, name='customer-detail'),
    path('jobs/', views.job_list_create, name='job-list-create'),  # List and create jobs
    path('jobs/<str:name>/', views.job_detail, name='job-detail'),
    
]    
