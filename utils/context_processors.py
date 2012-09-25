import datetime

def loaded(request):
    time = datetime.datetime.now()
    return {
        'time': time,
    }