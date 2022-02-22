import json
from django.shortcuts import render
from django.core import serializers as core_s
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework import permissions
from django.http import JsonResponse 
from .rest_serializers import *
from .forms import *
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
        model_list = core_s.serialize('json', HelloWorldModel.objects.all())    # turn the python object into JSON
        return HttpResponse(model_list, content_type="text/json-comment-filtered")


# Example handling a HTTP POST request
# clients will use a post reqeust to submit their data 
def postData(request):
    form = NameForm()
    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['your_name']
            new_record = HelloWorldModel(hello_world_str=data, model_info="The server saved the POST data!")
            new_record.save()
            return render(request, 'quick_api/showdata.html', {'data': data})
    return render(request, 'quick_api/submit.html', {'form': form})

# Example "home-page" that features a form with input boxes
# This template can be used for the user account site for the Delivery Detector
def exampleHomePage(request):
    home_form = HomePageForm()                  # load the home page form 
    if request.method == "POST":                # check if we got a POST request 
        home_form = HomePageForm(request.POST)  # populate a new form with the data sent from user
        if home_form.is_valid():
            # get the box with this PK
            box = BoxInfo.objects.get(pk=home_form.cleaned_data['box_number'])
            # create and save a new user
            new_user = UserAccount(user_name=home_form.cleaned_data['user_name'], 
                                   user_email=home_form.cleaned_data['user_email'],
                                   user_phone=home_form.cleaned_data['user_phone'],
                                   box_number=box)
            new_user.save()
            return render(request, 'quick_api/showuser.html', {'user': new_user})
    return render(request, 'quick_api/home_page.html', {'home_form': home_form})


# Example getting a user account from the DB and returing it to client
# Client devices will be using this in their API calls
def getUserWithPK(request, prim_key):
     user = UserAccount.objects.get(pk=prim_key)
     user_dict = model_to_dict(user) 
     return JsonResponse(json.loads(json.dumps(user_dict)))


# Check if the PK of the user supplied matches the box number
def checkUserBox(request, prim_key, box_numb):
    try:
        user = UserAccount.objects.get(pk=prim_key)
        box = BoxInfo.objects.get(pk=box_numb)
    except: 
        # one of the object below doesnt exist
        return JsonResponse(json.loads(json.dumps(["LOCK THE BOX!!!! THEY DONT MATCH"])), safe=False)
    if box_numb == user.box_number_id: # djagno stores the FK with _id at the end, so we can access it w/out going to the DB
        return JsonResponse(json.loads(json.dumps(["UNLOCK THE BOX!!!!"])), safe=False)
    else:
        return JsonResponse(json.loads(json.dumps(["LOCK THE BOX!!!! THEY DONT MATCH"])), safe=False)
