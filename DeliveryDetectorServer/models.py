from django.db import models

# Database table for user accounts    
class UserAccount(models.Model):
    user_name = models.CharField(max_length=200)
    user_pw = models.CharField(max_length=200)
    user_email = models.EmailField(max_length=300)
    user_phone = models.BigIntegerField()
    box_number = models.ForeignKey('BoxInfo', on_delete=models.CASCADE)

# Database table for boxes
class BoxInfo(models.Model): 
    box_number = models.IntegerField()
    date = models.DateField()
    multi_user = models.BooleanField()
    # need a one to many field or similar, to keep track of all users using this box

class OrderInfo(models.Model):
    order_number = models.BigIntegerField()
    user_name = models.CharField(max_length=200)
    seller_name = models.CharField(max_length=200)
    seller_email = models.EmailField(max_length=300)
    seller_phone = models.BigIntegerField()