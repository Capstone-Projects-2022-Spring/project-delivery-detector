from django.db import models

# Model class which corresponds to a database table
class HelloWorldModel(models.Model):
    hello_world_str = models.CharField(max_length=100)
    model_info = models.CharField(max_length=300)

#class UserAccount(models.Model):
    #first_name = models.CharField(max_length=100)
    #last_name = models.CharField(max_length=100)
    #will be adding other fields like email and phone number

#class BoxNumbers(models.Model):
    #will be adding other fields like serial number
