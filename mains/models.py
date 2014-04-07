from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Users can be friends
class Asker(models.Model):
    user = models.OneToOneField(User)
    friends = models.ManyToManyField('self',
                                     through='Relation',
                                     symmetrical=False,
                                     related_name='friend_to+',
                                     blank=True)
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
        return self.friends.filter(
            to_asker__from_asker=self
        )

    def __unicode__(self):
        return self.user.username

    def create_asker(sender, instance, created, **kwargs):
        if created:
            profile, created = Asker.objects.get_or_create(user=instance)
        return

    # Create a asker when a user is created
    post_save.connect(create_asker, sender=User)


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

    def __unicode__(self):
        return u"%s" % self.question_id
    def __str__(self):
        return self.question_text


class Answer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Asker)
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=80)

    def __unicode__(self):
        return u"%s" % self.answer_id

class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Asker)
    question_id = models.ForeignKey(Question)

    def __unicode__(self):
        return u"%s" % self.vote_id