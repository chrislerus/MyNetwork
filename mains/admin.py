from django.contrib import admin

from mains.models import Question, Answer, Asker, Vote

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Asker)
admin.site.register(Vote)