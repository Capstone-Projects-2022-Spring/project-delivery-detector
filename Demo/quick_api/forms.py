from django import forms

# Example form for "Hello-World" purposes
class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# Example form showing the use of different input areas
class HomePageForm(forms.Form):
    user_name = forms.CharField(label='User Account Name', max_length=200)
    user_email = forms.EmailField(max_length=300)
    user_phone = forms.IntegerField()
    box_number = forms.IntegerField()