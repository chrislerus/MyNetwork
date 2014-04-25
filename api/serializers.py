from mains.models import Question, Asker, Notification

from rest_framework import serializers

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'question_id',
            'question_text',
            'seeker',
            'target',
            'votes',
        )

        def restore_object(self, attrs, instance=None):
            question = Question(question_text=attrs['question_text'],
                                seeker=attrs['seeker'],
                                target=attrs['target'])
            return question

class AskerSerializer(serializers.ModelSerializer):
    pk = serializers.Field()
    class Meta:
        model = Asker
        fields = (
            'user',
            'kind_liked',
        )

class NotificationSerializer(serializers.ModelSerializer):
    pk = serializers.Field()
    class Meta:
        model = Notification
        fields = (
            'notif_id',
            'asker_id',
            'friend_id',
            'seen'
        )