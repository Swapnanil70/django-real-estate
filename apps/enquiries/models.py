from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TimeStampedUUIDModel
from phonenumber_field.modelfields import PhoneNumberField

class Enquiry(TimeStampedUUIDModel):
    name = models.CharField(verbose_name=_("Your Name"), max_length=100)
    phone_number = PhoneNumberField(verbose_name=_("Phone Number"), max_length=30, default='+639999999999')
    email = models.EmailField(verbose_name=_("Email"), max_length=255)
    subject = models.CharField(verbose_name=_("Subject"), max_length=100)
    message = models.TextField(verbose_name=_("Message"))

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = _("Enquiries")

