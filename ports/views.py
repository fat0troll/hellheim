from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from ports.models import Port, PortForm
from utils.decorators import is_staff
import datetime

@login_required
def ports_index(request):
    ports = Port.objects.all().order_by('vm')
    return render_to_response('ports/index.html', {
        'ports': ports,
    }, context_instance=RequestContext(request))

@is_staff
def add_port(request):
    """
    TODO: make it real!
    """
    user = request.user
    if request.method == "POST":
        form = PortForm(request.POST)
        if form.is_valid():
            new_port = form.save(commit=False)
            new_port.added_by = user
            new_port.save()
            return HttpResponseRedirect('/ports')
        else:
            return render_to_response('ports/add.html', {
                'form': form,
            }, context_instance=RequestContext(request))
    else:
        form = PortForm()
        return render_to_response('ports/add.html', {
            'form': form,
        }, context_instance=RequestContext(request))

@is_staff
def edit_port(request, pid):
    """
    TODO: make it real!
    """
    port = Port
    try:
        port = Port.objects.get(id=pid)
    except Port.DoesNotExist:
        raise Http404()
    if request.method == "POST":
        form = PortForm(request.POST, instance=port)
        if form.is_valid():
            port = form.save()
            port.last_modified = datetime.datetime.now()
            port.save()
            return HttpResponseRedirect('/ports')
        else:
            return render_to_response('ports/edit.html', {
                'form': form,
            }, context_instance=RequestContext(request))
    else:
        form = PortForm(instance=port)
        return render_to_response('ports/edit.html', {
            'form': form,
        }, context_instance=RequestContext(request))

@is_staff
def delete_port(request, pid):
    """
    TODO: make it real
    """
    try:
        port = Port.objects.get(id=pid)
    except Port.DoesNotExist:
        raise Http404()
    port.delete()
    return HttpResponseRedirect('/ports')