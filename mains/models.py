from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import utc
import logging

logger = logging.getLogger(__name__)

# Users can be friends
class Asker(models.Model):
    user = models.OneToOneField(User)
    friends = models.ManyToManyField('self',
                                     through='Relation',
                                     symmetrical=False,
                                     related_name='friend_to+',
                                     blank=True)
    type_liked = models.ManyToManyField('Type',
                                        related_name="+")
    creation_time = models.DateTimeField(default=datetime.now)
    last_time = models.DateTimeField(default=datetime.now)
    last_friend_add = models.DateTimeField(default=datetime.now)
    last_vote = models.DateTimeField(default=datetime.now)


    def add_relation(self, asker, first=True):
        relation, created = Relation.objects.get_or_create(
            from_asker=self,
            to_asker=asker
        )
        if first:
            asker.add_relation(self, False)
        return relation

    def del_relation(self, asker, first=True):
        Relation.objects.filter(
            from_asker=self,
            to_asker=asker
        ).delete()
        if first:
            asker.del_relation(self, False)
        return

    def get_friends(self):
        return self.friends.filter(to_asker__from_asker=self)

    def is_friend(self, asker):
        list_friend = self.friends.filter(to_asker__from_asker=self)
        return asker in list_friend

    def set_last_time(self):
        logger.warning("Set last time")
        self.last_time = datetime.now()
        self.save()

    def __unicode__(self):
        return self.user.username

    # Create a asker when a user is created


class Relation(models.Model):
    from_asker = models.ForeignKey(Asker, related_name='from_asker')
    to_asker = models.ForeignKey(Asker, related_name='to_asker')


# Visibility 0 = public, 1 = friends, 2 = me only
class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.CharField(max_length=80)
    seeker = models.ForeignKey(Asker, related_name='seeker')
    target = models.ForeignKey(Asker, related_name='target')
    type = models.CharField(max_length=10)
    visibility = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    trend_grade = models.FloatField(default=0)
    creation_time = models.DateTimeField(default=datetime.now())
    last_vote_time = models.DateTimeField(default=datetime.now())

    def set_last_vote_time(self):
        self.last_vote_time = datetime.now()
        self.save()
        return

    def set_trend_grade(self):
        delta_t = (datetime.utcnow().replace(tzinfo=utc) - self.last_vote_time).seconds
        self.trend_grade += (self.votes.__float__() / delta_t.__float__())
        self.set_last_vote_time()
        return

    def __unicode__(self):
        return u"%s" % self.question_id

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Asker)
    question_id = models.ForeignKey(Question)
    text = models.CharField(max_length=80)
    creation_time = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return u"%s" % self.answer_id


class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Asker, related_name="voter")
    question_id = models.ForeignKey(Question)
    creation_time = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return u"%s" % self.vote_id


class Genius(models.Model):
    genius_id = models.AutoField(primary_key=True)
    question_id = models.ForeignKey(Question, related_name="question")
    asker_id = models.ForeignKey(Asker, related_name="asker")
    rate = models.FloatField(default=0)
    rate_friends = models.FloatField(default=0)


# Type == 1 = Suggest Friends, 2 = Suggest vote, 3 = Old Connexion, 4 = Friends +1
# Level == Importance
class Notification(models.Model):
    notif_id = models.AutoField(primary_key=True)
    asker_id = models.ForeignKey('Asker', related_name="notified")
    friend_id = models.ForeignKey('Asker', related_name="notifier", null=True)
    type = models.IntegerField(default=0)
    seen = models.BooleanField(default=False)
    level = models.IntegerField(default=0)
    creation_time = models.DateTimeField(default=datetime.now())

class Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)