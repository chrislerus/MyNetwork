from django.conf.urls import patterns, include, url
from django.contrib import admin
from api import views
from django.conf.urls import include

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login/$', 'mains.views.login_user'),
    url(r'^$', 'mains.views.homepage'),
    url(r'^home/$', 'mains.views.homepage'),
    url(r'^new_user/$', 'mains.views.new_user'),
    url(r'^search/', 'mains.views.search'),
    url(r'^questions/all/$', 'mains.views.all_questions_by_time'),
    url(r'^questions/all/votes/$', 'mains.views.all_questions_by_votes'),
    url(r'^questions/all/(?P<question_id>\d+)/', 'mains.views.detail_answer'),
    url(r'^questions/all/votes/(?P<question_id>\d+)/', 'mains.views.detail_answer'),
    url(r'^questions/tome/$', 'mains.views.tome_questions_by_time'),
    url(r'^questions/tome/votes/$', 'mains.views.tome_questions_by_votes'),
    url(r'^questions/tome/(?P<question_id>\d+)/', 'mains.views.detail_answer'),
    url(r'^questions/all/votes/(?P<question_id>\d+)/', 'mains.views.detail_answer'),
    url(r'^rest/users/$', views.UserList.as_view()),
    url(r'^rest/users/(?P<pk>\d+)/$', views.UserDetails.as_view()),
    url(r'^rest/questions/$', views.QuestionList.as_view()),
    url(r'^rest/questions/(?P<question_id>\d+)/$', views.QuestionDetails.as_view()),
    url(r'^rest/users/(?P<pk>\d+)/friends/$', views.FriendList.as_view()),
    url(r'^(?P<username>[a-zA-Z0-9_.-]+)/$', 'mains.views.profile'),
)