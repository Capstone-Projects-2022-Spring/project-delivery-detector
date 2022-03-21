# refer back to the design doc. and add the fields mentioned there 
import json
from django.http import JsonResponse 
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.shortcuts import render
from .forms import *
from .models import *

# Home page view
def index(request):
    return render(request, 'DeliveryDetectorServer/index.html')

# Sign-up view
# Will provide a form for the user to fill out
# If the data is valid it will be saved to the production database 
def sign_up(request):
    form = UserAccountForm()
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['user_name']
            pw = form.cleaned_data['user_pw']
            email = form.cleaned_data['user_email']
            phone = form.cleaned_data['user_phone']
            box = BoxInfo.objects.get(pk=form.cleaned_data['box_number'])
            new_record = UserAccount(user_name=name, user_pw=pw, user_email=email, user_phone=phone, box_number=box)
            new_record.save()
            return HttpResponse("User has been added to the database!")
    return render(request, 'DeliveryDetectorServer/sign_up.html', {'form': form, 'title': 'Sign Up'})

# Log-in view
def log_in(request):
    form = LogInForm()
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['user_name']
            pw = form.cleaned_data['user_pw']
            user = UserAccount.objects.get(user_name=name, user_pw=pw)
            form = UserAccountForm()
            form.user_name = name
            form.user_pw = pw
            return render(request, 'DeliveryDetectorServer/sign_up.html', {'form': form, 'title': 'Change Settings'})
    return render(request, 'DeliveryDetectorServer/log_in.html', {'form': form})

def get_user(request, name):
     user = UserAccount.objects.get(user_name=name)
     user_dict = model_to_dict(user) 
     return JsonResponse(json.loads(json.dumps(user_dict)))
def wifi_QR(request):
    form = wifi_QR_form()
    if request.method == 'POST':
        form = wifi_QR_form(request.POST)
        if form.is_valid():
            name = form.cleaned_data['network_name']
            pw = form.cleaned_data['network_password']
            phone = form.cleaned_data['user_phone']
            return HttpResponse("Your QR code is on its way!")
    return render(request, 'DeliveryDetectorServer/wifi_QR.html', {'form': form})
