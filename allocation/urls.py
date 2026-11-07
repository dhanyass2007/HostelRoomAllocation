
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Login and Logout
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='allocation/login.html'
        ),
        name='login'
    ),

    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Student Registration
    path('register/', views.register, name='register'),

    # Admin Dashboard
    path(
        'dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # Block Management
    path('blocks/', views.block_list, name='block_list'),

    path(
        'blocks/add/',
        views.block_add,
        name='block_add'
    ),

    path(
        'blocks/edit/<int:pk>/',
        views.block_edit,
        name='block_edit'
    ),

    path(
        'blocks/delete/<int:pk>/',
        views.block_delete,
        name='block_delete'
    ),

    # Room Management
    path('rooms/', views.room_list, name='room_list'),

    path(
        'rooms/add/',
        views.room_add,
        name='room_add'
    ),

    path(
        'rooms/edit/<int:pk>/',
        views.room_edit,
        name='room_edit'
    ),

    path(
        'rooms/delete/<int:pk>/',
        views.room_delete,
        name='room_delete'
    ),

    # Student Dashboard
    path(
        'student/dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    # Student Room Request
    path(
        'room/request/<int:pk>/',
        views.room_request,
        name='room_request'
    ),

    # Admin Allocation Requests
    path(
        'allocation-requests/',
        views.allocation_requests,
        name='allocation_requests'
    ),

    # Approve / Reject
    path(
        'allocation-action/<int:pk>/<str:action>/',
        views.allocation_action,
        name='allocation_action'
    ),

]
