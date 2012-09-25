from django.shortcuts import render_to_response
from django.template import RequestContext

def main_page(request):
    return render_to_response('main.html', {

    }, context_instance=RequestContext(request))