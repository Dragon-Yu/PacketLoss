from django.http import HttpResponseRedirect


def redirect(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/fore_end/view/login/login.html")
    else:
        if (request.path == "/"):
            return HttpResponseRedirect("/fore_end/view/home/home.html")
        else:
            return HttpResponseRedirect("/fore_end" + request.path)
