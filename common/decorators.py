from django.http import HttpResponseRedirect

def loginRequired(function):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return wrapper

def logoutRequired(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/")
    return wrapper

def onlyUser(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.isAdmin and not request.user.isSuperuser:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/")
    return wrapper