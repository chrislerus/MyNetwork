from django.http import HttpResponse
from django.shortcuts import render
import logging
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework import permissions
from django.http import Http404
from api.serializers import QuestionSerializer, AskerSerializer
from api.permissions import IsSeekerOrReadOnly, IsUserOrReadOnly
from mains.models import Asker, Question

logger = logging.getLogger(__name__)


class UserList(generics.ListCreateAPIView):
    queryset = Asker.objects.all()
    serializer_class = AskerSerializer
    permission_classes = (permissions.IsAuthenticated,)

class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asker.objects.all()
    serializer_class = AskerSerializer
    permission_classes = (permissions.IsAuthenticated,IsUserOrReadOnly,)

class QuestionList(generics.ListCreateAPIView):
    queryset = Question.objects.order_by('-trend_grade')
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

class QuestionDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_field = 'question_id'
    permission_classes = (permissions.IsAuthenticated,IsSeekerOrReadOnly,)


class FriendList(APIView):
    def get_friends(self, pk):
        try:
            return Asker.objects.get(pk=pk).get_friends()
        except Asker.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        s = AskerSerializer(self.get_friends(pk))
        return Response(s.data)

    def post(self, request, pk, format=None):
        # TODO Create new relation
        return Http404
