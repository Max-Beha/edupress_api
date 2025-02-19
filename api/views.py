from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth import authenticate
from .models import User, Course, CourseSection, CourseMaterial, CourseEnrollment
from .serializers import (
    UserSerializer, RegisterSerializer, UserLoginSerializer,
    CourseSerializer, CourseSectionSerializer, CourseMaterialSerializer,
    CourseEnrollmentSerializer
)

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'teacher'
        )

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'student'
        )

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e.detail[0])},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class TeacherCourseView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        print("=== Debug Info ===")
        print(f"User: {self.request.user}")
        print(f"Is authenticated: {self.request.user.is_authenticated}")
        print(f"User type: {getattr(self.request.user, 'user_type', None)}")
        print(f"Auth header: {self.request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
        return Course.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class TeacherCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

class CourseSectionView(generics.ListCreateAPIView):
    serializer_class = CourseSectionSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return CourseSection.objects.filter(
            course__teacher=self.request.user,
            course_id=self.kwargs['course_pk']
        )

    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_pk'], teacher=self.request.user)
        serializer.save(course=course)

class CourseMaterialView(generics.ListCreateAPIView):
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return CourseMaterial.objects.filter(
            section__course__teacher=self.request.user,
            section_id=self.kwargs['section_pk']
        )

    def perform_create(self, serializer):
        section = CourseSection.objects.get(
            id=self.kwargs['section_pk'],
            course__teacher=self.request.user
        )
        serializer.save(section=section)

class CourseEnrollmentView(generics.CreateAPIView):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_id'])
        serializer.save(student=self.request.user, course=course)

class StudentEnrollmentListView(generics.ListAPIView):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return CourseEnrollment.objects.filter(student=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def update_course_progress(request, course_id):
    try:
        enrollment = CourseEnrollment.objects.get(
            student=request.user,
            course_id=course_id
        )
        progress = request.data.get('progress', 0)
        enrollment.progress = progress
        enrollment.save()
        return Response({'status': 'success'})
    except CourseEnrollment.DoesNotExist:
        return Response(
            {'error': 'Enrollment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
