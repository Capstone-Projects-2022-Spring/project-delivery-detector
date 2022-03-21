# refer back to the design doc. and add the fields mentioned there 
import os
import json
import urllib
import pyqrcode
import twilio
import twilio.rest
from django.core.files import File  
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from pyqrcode import QRCode
from twilio.rest import Client
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
            create_qr_code(name)
            qr = 'qr_' + name + '.png'
            box = BoxInfo.objects.get(pk=form.cleaned_data['box_number'])
            new_record = UserAccount(user_name=name, user_pw=pw, 
                                     user_email=email, user_phone=phone, 
                                     qr_code=qr, box_number=box)
            new_record.save()
            #os.remove(qr)
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

# Return a UserAccount record in JSON format 
def get_user(request, name):
    user = UserAccount.objects.get(user_name=name)
    dict = {'user_name': user.user_name, 'user_pw': user.user_pw,
            'user_email': user.user_email, 'user_phone': user.user_phone,
            'box_number': user.box_number.pk}
    return JsonResponse(json.loads(json.dumps(dict)))

# Generate QR code with the user name
def create_qr_code(name):
    qr_name = pyqrcode.create(name)
    qr_file_name = 'qr_' + name + '.png'
    qr_name.png(qr_file_name, scale=10)

# Send a delivery alert to the user 
def send_alert(request, name):
    # Get the UserAccount with the supplied name
    user = UserAccount.objects.get(user_name=name)
    phone = '1' + str(user.user_phone)
    qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + name
    email = user.user_email

    # send the email with the QR code 
    subject = 'Yoo Delivery Alert!!'
    message = 'You got a package fool!' + '\n' + qr_api_str
    #qr_code = bytes(user.qr_code.read())

    email = EmailMessage(
        subject,
        message,
        'deliverydetector@gmail.com',
        [email],
    )

    #email.attach('your_qr.png', qr_code, 'image/png')
    email.send()
    
    # send SMS with the QR code 
    account_sid = ''
    auth_token = ''
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                              body='Delivery Alert\n\nYou got a package fool!',
                              from_='+19033548375',
                              media_url=[qr_api_str],
                              to=phone
                          )

    return HttpResponse("Just sent an alert to Box-Owner!!")
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

