# ToDo
#
#  - REFACTOR!!
#
# refer back to the design doc. and add the fields mentioned there 
import os
import json
import urllib
import pyqrcode
import twilio
import twilio.rest
import random
from django.core.files import File  
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from pyqrcode import QRCode
from twilio.rest import Client
from .forms import *
from .models import *

# Twilio cred's
account_sid = 'AC92491224a3d8526f34d92c575f00cfc2'
auth_token = ''

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
                                     box_number=box)
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

# Clear an order number from the database
def clear_order_num(request, order_num):
    order = OrderInfo.objects.get(order_number=order_num)
    order.delete()
    return HttpResponse("Just removed order number: " + str(order_num))

# Return a UserAccount record in JSON format 
def get_user(request, name):
    user = UserAccount.objects.get(user_name=name)
    dict = {'user_name': user.user_name, 'user_pw': user.user_pw,
            'user_email': user.user_email, 'user_phone': user.user_phone,
            'box_number': user.box_number.pk}
    return JsonResponse(json.loads(json.dumps(dict)))

# Return a JSON list of all users assigned to a given box
def get_all_users(request, box_num):
    users = UserAccount.objects.all()
    all_users = {}
    count = 0
    for user in users:
        if user.box_number.pk == box_num:
            key = 'user' + str(count)
            count += 1
            all_users.update({key: user.user_name})
    return JsonResponse(json.loads(json.dumps(all_users)))

# Return a JSON list of all users assigned to a given box
# The client device will call this API at boot to get all the order numbers
def get_all_order_nums(request):
    orders = OrderInfo.objects.all()
    all_orders = {}
    index = 0
    for order in orders:
        # below is what the returned JSON looks like
        # the client device will reload the order numbers on boot 
        # {'0': [1111, max] }
        # {'1': [222, lewis] }
        all_orders.update({index: [order.order_number, order.user_name]})
        index += 1
    return JsonResponse(json.loads(json.dumps(all_orders)))

# Check if the user is registered to the order number
def check_order_num(request, name, order_num):
    try:
        order = OrderInfo.objects.get(order_number=order_num)
        result = 1 if order.user_name else 0
    except:
        result = 0
    ret_dict = {'check': result}
    return JsonResponse(json.loads(json.dumps(ret_dict)))

# Generate QR code with the user name
def create_qr_code(name):
    qr_name = pyqrcode.create(name)
    qr_file_name = 'qr_' + name + '.png'
    qr_name.png(qr_file_name, scale=10)

# Send a delivery alert to the user 
def send_alert(request, name, order_num):
    # Get the UserAccount with the supplied name
    user = UserAccount.objects.get(user_name=name)
    phone = '1' + str(user.user_phone)
    qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + name + '-' + str(order_num) + '-' + '0'
    email = user.user_email

    # send the email with the QR code 
    message = '\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner\n' + qr_api_str
    #qr_code = bytes(user.qr_code.read())

    email = EmailMessage(
        'Delivery Detector Alter',
        message,
        'deliverydetector@gmail.com',
        [email],
    )

    #email.attach('your_qr.png', qr_code, 'image/png')
    email.send()
    
    # send SMS with the QR code 
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                              body='\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner',
                              from_='+19033548375',
                              media_url=[qr_api_str],
                              to=phone
                          )

    return HttpResponse("Just sent an alert to Box-Owner!!\n" + str(message))

def send_alert_multi(request, name, order_num, slot_num):
    # Get the UserAccount with the supplied name
    user = UserAccount.objects.get(user_name=name)
    phone = '1' + str(user.user_phone)
    qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + name + '-' + str(order_num) + '-' + '0'
    email = user.user_email

    # send the email with the QR code 
    message = '\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner\n' + qr_api_str + '\n\nYour slot number is ' + str(slot_num)

    email = EmailMessage(
        'Delivery Detector - Package Dropoff',
        message,
        'deliverydetector@gmail.com',
        [email],
    )

    #email.attach('your_qr.png', qr_code, 'image/png')
    email.send()
    
    # send SMS with the QR code 
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                              body='\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner\n\nYour slot number is ' + str(slot_num),
                              from_='+19033548375',
                              media_url=[qr_api_str],
                              to=phone
                          )

    return HttpResponse("Just sent an alert to Box-Owner!!\n" + str(message))

# Wifi portal page
def wifi_QR(request):
    form = wifi_QR_form()
    if request.method == 'POST':
        form = wifi_QR_form(request.POST)
        if form.is_valid():
            name = form.cleaned_data['network_name']
            pw = form.cleaned_data['network_password']
            phone = "1" + str(form.cleaned_data['user_phone'])
            qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + 'wifi-' + name + '-' + pw

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body='\nHere is your QR Code, turn on your Delivery Detector and show this to the camera',
                from_='+19033548375',
                media_url=[qr_api_str],
                to=phone
            )

            return HttpResponse("Your QR code is on its way!")
    return render(request, 'DeliveryDetectorServer/wifi_QR.html', {'form': form})

def generate_order_number():
    order_number = ""
    numbers = [0,1,2,3,4,5,6,7,8,9]
    for i in range(10):
        order_number += str(random.choice(numbers))
    return order_number

def seller_QR(request):
    form = seller_QR_form()
    if request.method == 'POST':
        form = seller_QR_form(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data['user_name']
            seller_name = form.cleaned_data['seller_name']
            seller_email = form.cleaned_data['seller_email']
            seller_phone = '1' + str(form.cleaned_data['seller_phone'])
            order_num = generate_order_number()

            qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + user_name + '-' + order_num + '-1'
            client = Client(account_sid, auth_token)

            new_record = OrderInfo(user_name=user_name, order_number=order_num,
                                    seller_email=seller_email, seller_phone=seller_phone,
                                   seller_name=seller_name)
            new_record.save()
            message = client.messages.create(
                body='\nHere is your QR Code, turn on your Delivery Detector and show this to the camera',
                from_='+19033548375',
                media_url=[qr_api_str],
                to=seller_phone
            )

            subject = 'Delivery Detector'
            body = 'Here is the QR code you can attach to you package\n' + qr_api_str
            email = EmailMessage(
                subject,
                body,
                'deliverydetector@gmail.com',
                [seller_email],
            )
            email.send()

            return HttpResponse("Your QR code is on its way!")
    return render(request, 'DeliveryDetectorServer/seller_QR.html', {'form': form})

# Tampering API endpoint for client devices
def tamper_alert(request, name, alert_msg):
    # also refactor getting the user to a function
    #   - can do error-checking!
    # should refactor and have functions for sending alerts!
    error_dict = {'error': 'There is an error with your device!', 
                  'theft': 'Your package has been stolen!', 
                  'move': 'Your box has been moved!',
                  'open': 'Your box is open and can not close itself!'}
    user_email = UserAccount.objects.get(user_name=name).user_email
    user_phone = UserAccount.objects.get(user_name=name).user_phone


    subject = 'SECURIY ALERT - DELIVERY DETECTOR'
    for key in error_dict:
        if key == alert_msg:
            text_body = error_dict[key]

    client = Client(account_sid, auth_token)
            
    message = client.messages.create(
        body=text_body,
        from_='+19033548375',
        to=user_phone
    )

    email = EmailMessage(
        subject,
        text_body,
        'deliverydetector@gmail.com',
        [user_email],
    )
    email.send()
    return HttpResponse("Tampering alert has been sent!")
