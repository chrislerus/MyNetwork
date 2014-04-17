from mains.models import Question

from rest_framework import serializers

class QuestionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'question_id',
            'question_text',
            'seeker',
            'target',
            'votes',
            'creation_time'
        )