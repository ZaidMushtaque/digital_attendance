"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from attendance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Template Pages
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('report/', views.report_view, name='report'),
    
    # Auth APIs
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    
    # Profile APIs
    path('api/profile/', views.api_profile, name='api_profile'),
    path('api/profile/update/', views.api_profile_update, name='api_profile_update'),
    
    # Class APIs
    path('api/classes/', views.api_classes, name='api_classes'),
    path('api/classes/add/', views.api_class_add, name='api_class_add'),
    path('api/classes/<int:class_id>/rename/', views.api_class_rename, name='api_class_rename'),
    path('api/classes/<int:class_id>/delete/', views.api_class_delete, name='api_class_delete'),
    
    # Student APIs
    path('api/classes/<int:class_id>/students/add/', views.api_student_add, name='api_student_add'),
    path('api/students/<int:student_id>/edit/', views.api_student_edit, name='api_student_edit'),
    path('api/students/<int:student_id>/delete/', views.api_student_delete, name='api_student_delete'),
    
    # Attendance APIs
    path('api/students/<int:student_id>/attendance/', views.api_student_attendance, name='api_student_attendance'),
]

