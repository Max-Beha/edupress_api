from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import User, Course, CourseSection, CourseMaterial, CourseEnrollment
from .permissions import IsTeacher, IsStudent
from .serializers import (
    UserSerializer, RegisterSerializer, UserLoginSerializer,
    CourseSerializer, CourseSectionSerializer, CourseMaterialSerializer,
    CourseEnrollmentSerializer
)

@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with the provided details",
        responses={201: UserSerializer}
    )
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

@extend_schema(tags=['Authentication'])
class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Login user",
        description="Authenticate a user and return JWT tokens",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        }
    )
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

@extend_schema(tags=['User'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile"
    )
    def get_object(self):
        return self.request.user

@extend_schema(tags=['Courses'])
class TeacherCourseView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        summary="List/Create teacher courses",
        description="List all courses for the authenticated teacher or create a new course"
    )
    def get_queryset(self):
        print("=== Debug Info ===")
        print(f"User: {self.request.user}")
        print(f"Is authenticated: {self.request.user.is_authenticated}")
        print(f"User type: {getattr(self.request.user, 'user_type', None)}")
        print(f"Auth header: {self.request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
        return Course.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

@extend_schema(tags=['Courses'])
class TeacherCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        summary="Manage teacher course",
        description="Retrieve, update or delete a specific course"
    )
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

@extend_schema(tags=['Course Sections'])
class CourseSectionView(generics.ListCreateAPIView):
    serializer_class = CourseSectionSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        summary="List/Create course sections",
        description="List all sections for a course or create a new section"
    )
    def get_queryset(self):
        return CourseSection.objects.filter(
            course__teacher=self.request.user,
            course_id=self.kwargs['course_pk']
        )

    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_pk'], teacher=self.request.user)
        serializer.save(course=course)

@extend_schema(tags=['Course Materials'])
class CourseMaterialView(generics.ListCreateAPIView):
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        summary="List/Create course materials",
        description="List all materials for a section or create a new material"
    )
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

@extend_schema(tags=['Course Enrollment'])
class CourseEnrollmentView(generics.CreateAPIView):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Enroll in course",
        description="Enroll the authenticated student in a specific course"
    )
    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_id'])
        serializer.save(student=self.request.user, course=course)

@extend_schema(tags=['Course Enrollment'])
class StudentEnrollmentListView(generics.ListAPIView):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="List student enrollments",
        description="List all courses the authenticated student is enrolled in"
    )
    def get_queryset(self):
        return CourseEnrollment.objects.filter(student=self.request.user)

@extend_schema(
    tags=['Course Progress'],
    summary="Update course progress",
    description="Update the progress for a specific course enrollment",
    parameters=[
        OpenApiParameter(
            name="progress",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Progress percentage (0-100)"
        )
    ]
)
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
