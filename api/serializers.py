from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Course, CourseSection, CourseMaterial, CourseEnrollment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'bio', 'profile_picture', 'phone_number')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'user_type', 
                 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'password': {'write_only': True},
            'user_type': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if data['user_type'] not in ['student', 'teacher']:
            raise serializers.ValidationError({"user_type": "User type must be either 'student' or 'teacher'."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data['user'] = user
        return data

class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'teacher', 'teacher_name', 
                 'price', 'level', 'thumbnail', 'estimated_time', 
                 'materials_needed', 'is_published', 'created_at', 'updated_at')
        read_only_fields = ('teacher', 'created_at', 'updated_at')

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}" if obj.teacher else None

class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = ('id', 'title', 'order', 'course', 'created_at', 'updated_at')
        read_only_fields = ('course', 'created_at', 'updated_at')

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ('id', 'title', 'content_type', 'content_url', 
                 'order', 'section', 'created_at', 'updated_at')
        read_only_fields = ('section', 'created_at', 'updated_at')

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ('id', 'student', 'course', 'status', 'progress', 
                 'payment_id', 'created_at', 'updated_at')
        read_only_fields = ('student', 'created_at', 'updated_at')
