from rest_framework import serializers

from users.models import User

from .models import Course, Section, Resource, CourseStudent


class ElementSerializer(serializers.Serializer):
    """
        A serializer for course section elements, both text and video.

        Dynamically handles different types of content within a course section by specifying
        the element type, content, and its order within the section.

        Fields:
            type (CharField): The type of the element (text or video).
            content (CharField): The content of the element.
            order (IntegerField): The display order of the element within its section.
    """
    id = serializers.IntegerField()
    type = serializers.CharField()
    content = serializers.CharField()
    order = serializers.IntegerField()


class SectionSerializer(serializers.ModelSerializer):
    """
        Serializer for course sections, including nested serialization for text and video elements.

        Gathers and combines all elements (text and video) related to a section into a single, ordered list.

        Meta:
            model: The Section model that the serializer is associated with.
            fields: Specifies the fields of the Section model to be included in the serialization.

        Methods:
            get_elements: Combines text and video elements, sorting them by their order.
    """
    elements = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'name', 'elements']

    def get_elements(self, obj):
        text_elements = [{'id': elem.pk, 'type': 'text', 'content': elem.content,
                          'order': elem.order} for elem in obj.text_elements.all()]
        video_elements = [{'id': elem.pk, 'type': 'video', 'content': elem.content,
                           'order': elem.order} for elem in obj.video_elements.all()]
        combined = text_elements + video_elements
        combined_sorted = sorted(combined, key=lambda x: x['order'])

        return ElementSerializer(combined_sorted, many=True).data


class ResourceSerializer(serializers.ModelSerializer):
    """
        Serializer for external course resources.

        Handles serialization of course-related resources, such as reading materials or external links.

        Meta:
            model: The Resource model that the serializer is associated with.
            fields: Specifies the fields of the Resource model to be included in the serialization.
    """
    class Meta:
        model = Resource
        fields = ['id', 'name', 'url']


class CourseSerializer(serializers.ModelSerializer):
    """
        Serializer for the Course model, with nested serialization for sections, resources, and dynamic fields
        indicating if the current user is enrolled or teaching the course.

        Handles complex data presentation for courses, including detailed information about its structure
        and the user's relationship to the course.

        Meta:
            model: The Course model that the serializer is associated with.
            fields: Specifies all the fields of the Course model to be included in the serialization, along with
                    additional computed fields for user relationship to the course.

        Methods:
            get_enrolled: Checks if the user specified in the serializer's context is enrolled in the course.
            get_teaching: Checks if the user specified in the serializer's context is the teacher of the course.
            to_representation: Customizes the output representation based on 'preview' context, omitting certain fields.
    """
    enrolled = serializers.SerializerMethodField()
    teaching = serializers.SerializerMethodField()
    sections = SectionSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teacher', 'teacher_name',
                  'rating', 'enrolled', 'teaching', 'sections', 'resources']

    def get_enrolled(self, obj):
        user_id = self.context.get('user_id', None)
        return obj.student_enrolled(user_id)

    def get_teaching(self, obj):
        user_id = self.context.get('user_id', None)
        return obj.teacher.id == user_id

    def get_teacher_name(self, obj):
        teacher = obj.teacher
        return str(teacher)

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
    """
    Serializer for the relationship between a student and a course, including feedback and rating.

    Captures the enrollment status, textual and numeric feedback of a student for a course.

    Meta:
        model: The CourseStudent model that the serializer is associated with.
        fields: Specifies the fields of the CourseStudent model to be included in the serialization.

    Methods:
        is_enrolled: Checks if a student (by student_id) is enrolled in a specific course (by course_id).
    """
    feedback = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.IntegerField(
        min_value=1, max_value=10, required=False)

    class Meta:
        model = CourseStudent
        fields = ['student', 'course', 'feedback', 'rating']

    def is_enrolled(self, student_id: str, course_id: str):
        return CourseStudent.objects.filter(student__pk=student_id, course__pk=course_id).exists()
