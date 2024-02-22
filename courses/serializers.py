from rest_framework import serializers

from .models import Course, Section


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


class CourseSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = ['name', 'description', 'teacher_name', 'rating', 'sections']


class CoursePreviewSerializer(serializers.ModelSerializer):
    enrolled = serializers.SerializerMethodField()
    teaching = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['name', 'description', 'rating', 'enrolled', 'teaching']

    def get_enrolled(self, obj):
        user_id = self.context.get('user_id')
        return obj.student_enrolled(user_id)

    def get_teaching(self, obj):
        user_id = self.context.get('user_id')
        return obj.teacher.id == user_id
