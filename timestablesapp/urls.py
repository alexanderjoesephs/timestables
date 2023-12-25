from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('create_user',views.create_user,name='create_user'),
    path('login',views.user_login,name='user_login'),
    path('logout', views.logoutview, name='user_logout'),
    path('teacher_stats',views.teacher_stats,name='teacher_stats'),
    path('teacher_set_work',views.teacher_set_work,name='teacher_set_work'),
    path('teacher_print_flashcards',views.teacher_print_flashcards,name='teacher_print_flashcards'),
    path('teacher_download_pdf_from=<str:date_from>&to=<str:date_to>',views.teacher_download_pdf,name='teacher_download_pdf'),
    path('play', views.play, name='play'),
    path('play_all',views.play_all,name='play_all'),
    path('create_attempt', views.create_attempt, name='create_attempt'),
    path('student',views.student,name='student'),
    path('student_play',views.student_play,name='student_play'),
    path('student_ready',views.student_ready,name='student_ready'),
    path('admin',views.admin,name='admin')
    ]
"""
    path('teach', views.teach, name='teach'),
    path('add_students', views.add_students, name='add_students'),
    path('remove_students', views.remove_students, name='remove_students'),
    path('stats', views.stats, name='stats'),
    path('stats/<str:student>',views.student_stats,name='student_stats'),
    path('stats/<str:student>/flash', views.flash, name='flash'),
    path('stats_set/<str:student>',views.student_stats_set,name='student_stats_set'),
    path('stats_set/<str:student>/flash',views.flash_set,name='flash_set'),
    path('class_flash',views.class_flash,name='class_flash'),
    path('class_stats',views.class_stats,name='class_stats'),
    path('student_view_stats_all',views.student_view_stats_all,name='student_view_stats_all'),
    path('student_view_stats_set',views.student_view_stats_set,name='student_view_stats_set'),
    """



    
