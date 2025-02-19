from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, UserProfileView,
    TeacherCourseView, TeacherCourseDetailView,
    CourseSectionView, CourseMaterialView,
    CourseEnrollmentView, StudentEnrollmentListView,
    update_course_progress
)

app_name = 'api'

urlpatterns = [
    # Authentication URLs
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Teacher URLs
    path('teacher/courses/', TeacherCourseView.as_view(), name='teacher-courses'),
    path('teacher/courses/<int:pk>/', TeacherCourseDetailView.as_view(), name='teacher-course-detail'),
    path('teacher/courses/<int:course_pk>/sections/', CourseSectionView.as_view(), name='course-sections'),
    path('teacher/sections/<int:section_pk>/materials/', CourseMaterialView.as_view(), name='section-materials'),

    # Student URLs
    path('student/courses/<int:course_id>/enroll/', CourseEnrollmentView.as_view(), name='course-enroll'),
    path('student/enrollments/', StudentEnrollmentListView.as_view(), name='student-enrollments'),
    path('student/courses/<int:course_id>/progress/', update_course_progress, name='update-progress'),
]
