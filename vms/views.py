from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from utils.decorators import is_staff
from vms.models import VirtualMachine, VMForm
from django.template.context import RequestContext

@login_required
def machine_index(request):
    vms = VirtualMachine.objects.all().order_by('name')
    return render_to_response('vms/index.html', {
        'vms': vms,
    }, context_instance=RequestContext(request))

@is_staff
def add_machine(request):
    """
    TODO: need some magic to make VM 'real' not just 'visible on site'!
    """
    if request.method == "POST":
        form = VMForm(request.POST)
        if form.is_valid():
            new_vm = form.save()
            new_vm.save()
            return HttpResponseRedirect('/vms')
        else:
            return render_to_response('vms/add.html', {
                'form': form,
            }, context_instance=RequestContext(request))
    else:
        form = VMForm()
        return render_to_response('vms/add.html', {
            'form': form,
        }, context_instance=RequestContext(request))

@is_staff
def edit_machine(request, pid):
    """
    TODO: need some magic to make VM editing 'real', not just 'visible on site!'
    """
    vm = VirtualMachine
    try:
        vm = VirtualMachine.objects.get(id=pid)
    except VirtualMachine.DoesNotExist:
        raise Http404()
    if request.method == "POST":
        form = VMForm(request.POST, instance=vm)
        if form.is_valid():
            vm = form.save()
            vm.save()
            return HttpResponseRedirect('/vms')
        else:
            return render_to_response('vms/edit.html', {
                'form': form,
            }, context_instance=RequestContext(request))
    else:
        form = VMForm(instance=vm)
        return render_to_response('vms/edit.html', {
            'form': form,
        }, context_instance=RequestContext(request))