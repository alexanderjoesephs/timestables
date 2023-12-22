from django.urls import path
from . import views

urlpatterns = [
    path('', views.myview),
    path('create_user',views.create_user,name='create_user'),
    path('login',views.user_login,name='user_login'),
    path('logout', views.logoutview, name='user_logout'),
    path('play', views.play, name='play'),
    path('play_all',views.play_all,name='play_all'),
    path('create_attempt', views.create_attempt, name='create_attempt'),
    path('teach', views.teach, name='teach'),
    path('add_students', views.add_students, name='add_students'),
    path('remove_students', views.remove_students, name='remove_students'),
    path('stats', views.stats, name='stats'),
    path('stats/<str:student>',views.student_stats,name='student_stats'),
    path('stats/<str:student>/flash', views.flash, name='flash'),
    path('stats_set/<str:student>',views.student_stats_set,name='student_stats_set'),
    path('stats_set/<str:student>/flash',views.flash_set,name='flash_set'),
    path('class_flash',views.class_flash,name='class_flash'),
    path('class_stats',views.class_stats,name='class_stats')

]