from django.shortcuts import render
from django.core import serializers as core_s
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .rest_serializers import *
from . import models


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')  # get all the User records from the DB 
    serializer_class = UserSerializer                       # the fields associated with the User we want to return 


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()       
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]  


class HelloWorldSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the HelloWorldModel db table to be viewed or edited.
    """
    queryset = HelloWorldModel.objects.all()
    serializer_class = HelloWorldSerializer

    # Handle a HTTP get request, like an API call from a client 
    def get(self, request):
        model = HelloWorldModel.objects.all()
        model_list = core_s.serialize('json', model)
        return HttpResponse(model_list, content_type="text/json-comment-filtered")
