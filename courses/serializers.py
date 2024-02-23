from rest_framework import serializers

from users.models import User

from .models import Course, Section, Resource, CourseStudent


class ElementSerializer(serializers.Serializer):
    type = serializers.CharField()
    content = serializers.CharField()
    order = serializers.IntegerField()


class SectionSerializer(serializers.ModelSerializer):
    elements = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['name', 'elements']

    def get_elements(self, obj):
        text_elements = [{'type': 'text', 'content': elem.content,
                          'order': elem.order} for elem in obj.text_elements.all()]
        video_elements = [{'type': 'video', 'content': elem.content,
                           'order': elem.order} for elem in obj.video_elements.all()]
        combined = text_elements + video_elements
        combined_sorted = sorted(combined, key=lambda x: x['order'])

        return ElementSerializer(combined_sorted, many=True).data


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['name', 'url']


class CourseSerializer(serializers.ModelSerializer):
    enrolled = serializers.SerializerMethodField()
    teaching = serializers.SerializerMethodField()
    sections = SectionSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teacher_name',
                  'rating', 'enrolled', 'teaching', 'sections', 'resources']

    def get_enrolled(self, obj):
        user_id = self.context.get('user_id', None)
        return obj.student_enrolled(user_id)

    def get_teaching(self, obj):
        user_id = self.context.get('user_id', None)
        return obj.teacher.id == user_id

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if (self.context.get('preview', False)):
            data.pop('sections', None)
            data.pop('resources', None)
        else:
            data.pop('enrolled', None)
            data.pop('teaching', None)
        return data


class CourseStudentSerializer(serializers.ModelSerializer):
    feedback = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.IntegerField(
        min_value=1, max_value=10, required=False)

    class Meta:
        model = CourseStudent
        fields = ['student', 'course', 'feedback', 'rating']

    def is_enrolled(self, student_id: str, course_id: str):
        return CourseStudent.objects.filter(student__pk=student_id, course__pk=course_id).exists()
