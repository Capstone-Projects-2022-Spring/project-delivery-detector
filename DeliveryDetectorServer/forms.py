from django import forms

# Form for the sign up page
class UserAccountForm(forms.Form):
    user_name = forms.CharField(label='User Account Name', max_length=200)
    user_pw = forms.CharField(label='Password', max_length=200)
    user_email = forms.EmailField(max_length=300)
    user_phone = forms.IntegerField()
    box_number = forms.IntegerField()

# Form for the log in page
class LogInForm(forms.Form):
    user_name = forms.CharField(label='User Account Name', max_length=200)
    user_pw = forms.CharField(label='Password', max_length=200)