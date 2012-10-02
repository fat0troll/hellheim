from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext as _

class VirtualMachine(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=5120, help_text=_("Some descriptive description"))
    ip_addr = models.IPAddressField(help_text=_("Machine's IP address"))
    mac_addr = models.CharField(max_length=17, help_text=_("Machine's MAC address"))
    owner = models.ForeignKey(User, help_text=_('Administrator of the virtual machine'))
    last_modified = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class VMForm(ModelForm):
    class Meta:
        model = VirtualMachine
