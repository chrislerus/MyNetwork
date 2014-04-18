from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from mains.serializers import QuestionSerializers
from mains.models import Answer, Question, Asker, Vote
from mains.signals import *

import logging

logger = logging.getLogger(__name__)

# Login page. Mandatory
def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        current_user = authenticate(username=username, password=password)
        if current_user is not None:
            if current_user.is_active:
                login(request, current_user)
                return HttpResponseRedirect('/home/')
    return render_to_response('mains/login.html',
                              context_instance=RequestContext(request))

def new_user(request):
    if request.POST:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        User.objects._create_user(username, email, password, is_staff=False, is_superuser=False)
        logger.warning("Save User")
        return HttpResponseRedirect('/login/')
    return render_to_response('mains/new_user.html',
        {},
                              context_instance=RequestContext(request))

# Home. Ask a question to a asker.
# TODO : Find a way to stock Asker instance
@login_required(login_url='/login/')
def homepage(request):
    if request.POST:
        quest_text = request.POST['question']
        target = request.POST['target']
        current_seeker = Asker.objects.get(user__username__exact=request.user)
        current_target = Asker.objects.get(user__username__exact=target)
        Question.objects.create(question_text=quest_text, seeker=current_seeker, target=current_target, )
        return HttpResponseRedirect('/home/')
    return render_to_response('mains/homepage.html',
                              {'page_title': 'Welcome', 'current_user': request.user},
                              context_instance=RequestContext(request))


# Display friends. Not handled if no user
# ownprofile: 1 = myself, 2 = already friends, 3 = nobody
def profile(request, username):
    current_profile = Asker.objects.get(user__username__exact=username)
    log_in_asker = Asker.objects.get(user__username__exact=request.user)
    if 'btn_friend' in request.POST:
        log_in_asker.add_relation(current_profile)
    if 'btn_unfriend' in request.POST:
        log_in_asker.del_relation(current_profile)
    if 'question' in request.POST:
        quest_text = request.POST['question']
        Question.objects.create(question_text=quest_text, seeker=log_in_asker, target=current_profile)
    if current_profile:
        l_friends = current_profile.get_friends()
    if current_profile.user == request.user:
        own_profile = 1
    elif log_in_asker in l_friends:
        own_profile = 2
    else:
        own_profile = 3
    return render_to_response('mains/profile.html',
                              {'l_friends': l_friends, 'page_title': "My Profile", 'current_user': request.user,
                               'profile': current_profile, 'own_profile': own_profile},
                              context_instance=RequestContext(request)
    )


# Display all questions
def all_questions_by_votes(request):
    l_quests = Question.objects.exclude(target=request.user.id).order_by('-votes')
    return render_to_response('mains/questions_votes.html',
                              {"l_quests": l_quests, "page_title": "Questions World", 'current_user': request.user},
                              context_instance=RequestContext(request))


# Display question to vote ordered by time (Id)
def all_questions_by_time(request):
    l_quests = Question.objects.exclude(target=request.user.id).order_by('-question_id')
    return render_to_response('mains/questions_votes.html',
                              {"l_quests": l_quests, "page_title": "Questions World", 'current_user': request.user},
                              context_instance=RequestContext(request))


# Display questions asked by people, ordered by votes
def tome_questions_by_votes(request):
    l_quests = Question.objects.filter(target=request.user.id).order_by('-votes')
    return render_to_response('mains/questions_answers.html',
                              {"l_quests": l_quests, "page_title": "Questions To Me", 'current_user': request.user},
                              context_instance=RequestContext(request))


# Display questions asked by people, ordered by time (Id)
def tome_questions_by_time(request):

    l_quests = Question.objects.filter(target=request.user.id).order_by('-question_id')
    return render_to_response('mains/questions_answers.html',
                              {"l_quests": l_quests, "page_title": "Questions To Me", 'current_user': request.user},
                              context_instance=RequestContext(request))


# TODO : Disable button if already voted. How? check vote table
def detail_answer(request, question_id):
    current_quest = Question.objects.get(pk=question_id)
    answers = Answer.objects.filter(question_id=current_quest)
    current_asker = Asker.objects.get(user__username__exact=request.user)
    if request.POST:
        if 'btn_vote' in request.POST:
            Vote.objects.create(user_id=current_asker, question_id=current_quest)
        elif 'btn_answer' in request.POST:
            Answer.objects.create(user_id=current_asker, question=current_quest, text=request.POST['answer'])
            return HttpResponseRedirect('questions/tome/')
    return render_to_response('mains/question_details.html',
                              {"quest": current_quest, "page_title": "Detail Question", "answers": answers, 'current_user': request.user},
                              context_instance=RequestContext(request))


def search(request):
    if 'search' in request.POST:
        req_search = request.POST['search']
        l_quest = Question.objects.filter(question_text__icontains=req_search)
        l_user = Asker.objects.filter(user__username__icontains = req_search)
    return render_to_response('mains/search.html',
                              {'req_search': req_search, 'current_user': request.user, 'l_quest': l_quest, 'l_user': l_user},
                              context_instance=RequestContext(request))


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def question_list(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer = QuestionSerializers(questions, many=True)
        return JSONResponse(serializer.data)
    elif request.method == 'POST':
        data = JSONParser.parse(request)
        serializer = QuestionSerializers(data=data)
        try:
            serializer.save_object()
            return JSONResponse(serializer.data, status=201)
        except:
            return JSONResponse(serializer._errors, status=400)
