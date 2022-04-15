"""
    Django views for the DeliveryDetectorServer

    This file acts as a 'middleman' in between the server and client
    These functions will handle the differnet API calls 
"""
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
            box = get_box_object(form)
            if box != 0:
                new_record = UserAccount(user_name=name, user_pw=pw, 
                                     user_email=email, user_phone=phone, 
                                     box_number=box)
                new_record.save()
                return HttpResponse("User has been added to the database!")
            else:
                return HttpResponse("Error: no such box exists!")
    return render(request, 'DeliveryDetectorServer/sign_up.html', {'form': form, 'title': 'Sign Up'})


# Safely get a box object from the database
def get_box_object(form):
    try:
        box = BoxInfo.objects.get(pk=form.cleaned_data['box_number'])
    except:
        box = 0
    return box


# Log-in view
def log_in(request):
    form = LogInForm()
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['user_name']
            pw = form.cleaned_data['user_pw']
            user = get_user_safe(name)
            if user != 0:
                form = UserAccountForm()
                form.user_name = name
                form.user_pw = pw
                return render(request, 'DeliveryDetectorServer/sign_up.html', {'form': form, 'title': 'Change Settings'})
            else:
                return HttpResponse("Error: no such user exists!")
    return render(request, 'DeliveryDetectorServer/log_in.html', {'form': form})


# Safely get a user from the database
def get_user_safe(name):
    try:
        print('\nTRYING TO GET USER\n')
        user = UserAccount.objects.get(user_name=name)
    except:
        user = 0
    return user


# Clear an order number from the database
def clear_order_num(request, order_num):
    try:
        order = OrderInfo.objects.get(order_number=order_num)
        order.delete()
        return HttpResponse("Just removed order number: " + str(order_num))
    except:
        return HttpResponse("Order number: " + str(order_num) + " does not exist")


# Return a UserAccount record in JSON format 
def get_user(request, name):
    user = get_user_safe(name)
    if user != 0:
        dict = {'user_name': user.user_name, 'user_pw': user.user_pw,
                'user_email': user.user_email, 'user_phone': user.user_phone,
                'box_number': user.box_number.pk}
        return JsonResponse(json.loads(json.dumps(dict)))
    else:
        return HttpResponse("Error getting user!")


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
    user = get_user_safe(name)
    if user == 0:
        return HttpResponse("Error, no user exists!")
    phone = '1' + str(user.user_phone)
    qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + name + '-' + str(order_num) + '-' + '0'
    email = user.user_email
    body='\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner'
    subject = 'Delivery Detector Alert'
    send_alert_util(phone, email, body, subject, qr_api_str)
    return HttpResponse("Just sent an alert to Box-Owner!!\n" + str(message))


def send_alert_multi(request, name, order_num, slot_num):
    # Get the UserAccount with the supplied name
    user = get_user_safe(name)
    if user == 0:
        return HttpResponse("Error, no user exists!")
    phone = '1' + str(user.user_phone)
    qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + name + '-' + str(order_num) + '-' + '0'
    email = user.user_email
    body='\nDelivery Alert\n\nYou got a package fool!\n\nPresent the QR code to the Delivery Detector Scanner\n\nYour slot number is ' + str(slot_num),
    subject = 'Delivery Detector - Package Dropoff'
    send_alert_util(phone, email, body, subject, qr_api_str)
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

# Generate a 10-digit psuedo-random order number
def generate_order_number():
    order_number = ""
    numbers = [0,1,2,3,4,5,6,7,8,9]
    for i in range(10):
        order_number += str(random.choice(numbers))
    return order_number


# Seller portal
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
            subject = 'Delivery Detector - Seller QR'
            qr_api_str = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + user_name + '-' + str(order_num) + '-1'
            client = Client(account_sid, auth_token)

            new_record = OrderInfo(user_name=user_name, order_number=order_num,
                                    seller_email=seller_email, seller_phone=seller_phone,
                                   seller_name=seller_name)
            new_record.save()
            body = '\nHere is your QR Code, turn on your Delivery Detector and show this to the camera\n'
            send_alert_util(seller_phone, seller_email, body, subject, qr_api_str)
            return HttpResponse("Your QR code is on its way!")
    return render(request, 'DeliveryDetectorServer/seller_QR.html', {'form': form})


# Tampering API endpoint for client devices
def tamper_alert(request, name, alert_msg):
    # mapping of error messages
    error_dict = {'error': '\nThere is an error with your device!', 
                  'theft': '\nYour package has been stolen!', 
                  'move': '\nYour box has been moved!',
                  'qr': '\nA delivery person is re-using a QR-code to get into the box!',
                  'open': '\nYour box is open and can not close itself!'}

    user = get_user_safe(name)
    if user == 0:
        return HttpResponse("Error, no user exists!")

    user_email = user.user_email
    user_phone = user.user_phone

    subject = 'SECURIY ALERT - DELIVERY DETECTOR'
    if alert_msg in error_dict.keys():
        text_body = error_dict[alert_msg]
    else:
        text_body = 'error'

    send_alert_util(user.user_phone, user.user_email, text_body, subject)
    return HttpResponse("Tampering Alert has been sent!")


# Helper function to send SMS and email alerts 
def send_alert_util(user_phone, user_email, text_body, subject, media=""):
    # Twilio used for SMS
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=text_body,
        from_='+19033548375',
        media_url=[media],
        to=user_phone
    )
    
    # Email alert
    email_msg = text_body + '\n' + media
    email = EmailMessage(
        subject,
        email_msg,
        'deliverydetector@gmail.com',
        [user_email],
    )
    email.send()
