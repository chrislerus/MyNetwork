from django.shortcuts import render, render_to_response, redirect
from mains.models import Answer, Question, User, Asker
from django.http import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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

# Home. Ask a question to a asker.
# TODO : Find a way to stock Asker instance
@login_required(login_url='/login/')
def homepage(request):
    if request.POST:
        quest_text = request.POST['question']
        target = request.POST['target']
        for asker in Asker.objects.all():
            if asker.user.username == target:
                current_target = asker
            if asker.user == request.user:
                current_seeker = asker
        Question.objects.create(question_text = quest_text, seeker=current_seeker, target=current_target)
        return HttpResponseRedirect('/home/')
    return render_to_response('mains/homepage.html',
                              {'page_title': 'Welcome', 'current_user': request.user},
                              context_instance=RequestContext(request))

# Display friends. Not handled if no user
def friends(request):
    for asker in Asker.objects.all():
        if request.user == asker.user:
            current_user = asker
            break
    l_friends = current_user.friends.all()
    return render_to_response('mains/friends.html',
        {'l_friends': l_friends, 'page_title': "My Profile"},
        context_instance=RequestContext(request)
        )

# Display all questions
def all_questions_by_votes(request):
    l_quests = Question.objects.exclude(target=request.user.id).order_by('-votes')
    return render_to_response('mains/questions_votes.html',
        {"l_quests": l_quests, "page_title": "Questions World"},
        context_instance=RequestContext(request))

# Display question to vote ordered by time (Id)
def all_questions_by_time(request):
    l_quests = Question.objects.exclude(target=request.user.id).order_by('-question_id')
    return render_to_response('mains/questions_votes.html',
        {"l_quests": l_quests, "page_title": "Questions World"},
        context_instance=RequestContext(request))

# Display questions asked by people, ordered by votes
def tome_questions_by_votes(request):
    l_quests = Question.objects.filter(target=request.user.id).order_by('-votes')
    return render_to_response('mains/questions_answers.html',
        {"l_quests": l_quests, "page_title": "Questions To Me"},
        context_instance=RequestContext(request))

# Display questions asked by people, ordered by time (Id)
def tome_questions_by_time(request):

    l_quests = Question.objects.filter(target=request.user.id).order_by('-question_id')
    return render_to_response('mains/questions_answers.html',
        {"l_quests": l_quests, "page_title": "Questions To Me"},
        context_instance=RequestContext(request))

def detail_answer(request, question_id):
    quest = Question.objects.get(pk=question_id)
    answers = Answer.objects.all()
    if request.POST:
        for asker in Asker.objects.all():
            if asker.user == request.user:
                current_asker = asker
        current_quest = Question.objects.get(pk=question_id)
        Answer.objects.create(user_id=current_asker, question=current_quest, text=request.POST['answer'])
        return HttpResponseRedirect('questions/tome/')
    return render_to_response('mains/question_detail_answer.html',
        {"quest": quest, "page_title": "Detail Question", "answers": answers},
        context_instance=RequestContext(request))