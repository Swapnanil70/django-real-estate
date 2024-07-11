from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        error_class = 'error'
        

class CustomUserChangeForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        error_class = 'error'