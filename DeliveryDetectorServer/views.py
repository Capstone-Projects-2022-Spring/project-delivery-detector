# refer back to the design doc. and add the fields mentioned there 
import json
import pyqrcode
from pyqrcode import QRCode
from django.http import JsonResponse 
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.core.mail import EmailMessage
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

# Return a UserAccount record in JSON format 
def get_user(request, name):
    user = UserAccount.objects.get(user_name=name)
    user_dict = model_to_dict(user) 
    return JsonResponse(json.loads(json.dumps(user_dict)))

# Send a delivery alert to the user 
def send_alert(request, name):
    # Get the UserAccount with the supplied name
    user = UserAccount.objects.get(user_name=name)
    phone = user.user_phone
    email = user.user_email
    # Generate QR code with the user name
    url = pyqrcode.create(name)
    # Create and save the png file naming "myqr.png"
    qr_name = 'qr_' + name + '.png'
    url.png(qr_name, scale = 6)
    # Send an Email
    send_email = EmailMessage(
        subject='Delivery Detector Alert',
        body='This is an alert from the Delivery Detector. Please use the QR-Code provided to open the box',
        from_email='johnglatts1@hotmail.com',
        to=[email],
        #attachments=(qr_name, url, 'image/png')
    )
    send_email.send()
    # Send a SMS
    # To-Do
    # need to set-up a Twilio account - https://www.twilio.com/docs/sms/quickstart/python
    return HttpResponse("Just sent an alert to Box-Owner!!")


