# import the standard Django Forms 
# from built-in library 
from django import forms  
from django.forms import ModelForm, TextInput, EmailInput
    
# creating a form   
class InputForm(forms.Form):   
    movie_name = forms.CharField(label="",max_length=100,widget=forms.TextInput(attrs={"class": "form-control","placeholder": "Enter the movie name"}))
