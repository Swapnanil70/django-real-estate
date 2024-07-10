from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

# Custom User Manager : Create User
class CustomUserManager(BaseUserManager):
    
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))
        
    def create_user(self, username, first_name, last_name, email, password=None, **extra_fields):
        if not username:
            raise ValueError(_("The Username field must be filled"))
        
        if not first_name:
            raise ValueError(_("The First Name field must be filled"))
        
        if not last_name:
            raise ValueError(_("The Last Name field must be filled"))
        
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Base User Account : You must provide an email address"))
            
        user = self.model(username=username, 
                          email=email, 
                          first_name=first_name, 
                          last_name=last_name, 
                          **extra_fields)
        
        user.set_password(password)
        extra_fields.setdefault('is_staff', False) # Default value for is_staff is False
        extra_fields.setdefault('is_superuser', False) # Default value for is_superuser is False
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))
        
        if not password:
            raise ValueError(_("Superuser must have a password"))
        
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Admin Account : You must provide an email address"))
        
        user = self.create_user(username, first_name, last_name, email, password, **extra_fields)
        user.save(using=self._db)
        return user
        
        