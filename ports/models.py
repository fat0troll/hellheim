from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from vms.models import VirtualMachine

class Port(models.Model):
    number_in = models.CharField(max_length=40, help_text=_('Internal port number(s)'))
    number_out = models.CharField(max_length=40, help_text=_('External port number(s)'))
    added_by = models.ForeignKey(User, editable=False)
    vm = models.ForeignKey(VirtualMachine)
    last_modified = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return "%s -> %s" % (self.number_in, self.number_out)

class PortForm(ModelForm):
    class Meta:
        model = Port