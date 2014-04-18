from mains.models import Asker, Vote, Notification, Relation, Question
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from datetime import datetime
from django.utils.timezone import utc

import logging

logger = logging.getLogger(__name__)

# Create a asker when a user is created
@receiver(post_save, sender=User)
def create_asker(sender, instance, created, **kwargs):
    logger.warning("Create asker signal")
    if created:
        profile, created = Asker.objects.get_or_create(user=instance)
    return

@receiver(user_logged_in)
def logged_in(sender, request, user, **kwargs):
    logger.warning("User log in")
    current_asker = Asker.objects.get(user__username__exact=user.username)
    if (datetime.utcnow().replace(tzinfo=utc) - current_asker.last_friend_add).seconds > 60:
        Notification.objects.get_or_create(asker_id=current_asker, type=1)
        logger.warning("Notif created : Suggest friends")
    if (datetime.utcnow().replace(tzinfo=utc) - current_asker.last_vote).seconds > 60:
        Notification.objects.get_or_create(asker_id=current_asker, type=2)
        logger.warning("Notif created : Suggest Vote")
    if (datetime.utcnow().replace(tzinfo=utc) - current_asker.last_time).seconds > 60:
        Notification.objects.get_or_create(asker_id=current_asker, type=3)
        logger.warning("Notif created : Long time not seeing you!")
        logger.warning((datetime.utcnow().replace(tzinfo=utc) - current_asker.last_time).seconds)
    return

@receiver(user_logged_out)
def logged_out(sender, request, user, **kwargs):
    logger.warning("User log out")
    try:
        current_asker = Asker.objects.get(user__username__exact=user.username)
        current_asker.set_last_time()
    except:
        pass
    return

@receiver(post_save, sender=Question)
def question_created(sender, instance, created, **kwargs):
    if created:
        logger.warning("Notif TODO : Question is created")


@receiver(post_save, sender=Vote)
def vote_created(sender, instance, created, **kwargs):
    if created:
        logger.warning("Notif TODO : Vote is created")
        current_quest = instance.question_id
        current_quest.votes += 1
        current_quest.save()
        # TODO Create notif of a vote AND Check if 10 votes
        if current_quest.votes > 9:
            logger.warning("------------- Question trendy ", current_quest.votes)
        else:
            logger.warning("------------- Question new ", current_quest.votes)
        # Create notif type friend if its a friend
        if instance.question_id.seeker.is_friend(current_quest.target):
            logger.warning("-----------------its a friend")
            Notification.objects.get_or_create(asker_id=current_quest.target,
                                               friend_id=current_quest.seeker,
                                               type=4)
        # calculate trend_grade question
        Question.set_trend_grade(instance.question_id)

@receiver(post_save, sender=Relation)
def relation_created(sender, instance, created, **kwargs):
    if created:
        # TODO Create notif of a new relation
        logger.warning("Notif TODO : A new Relation is created")
