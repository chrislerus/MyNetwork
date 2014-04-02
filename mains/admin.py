from django.contrib import admin

from mains.models import Question, Answer, Asker

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Asker)