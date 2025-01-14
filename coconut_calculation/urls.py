from django.urls import path
from . import views



urlpatterns = [
    path('customers/', views.customer_list, name='customer-list'),
    path('customers/<str:id>/', views.customer_detail, name='customer-detail'),  # Use 'id' instead of 'mobile_number'
    path('jobs/', views.job_list_create, name='job-list-create'),  # List and create jobs
    path('jobs/<str:id>/', views.job_detail, name='job-detail'),  # Use 'id' for job details
]

    
  
