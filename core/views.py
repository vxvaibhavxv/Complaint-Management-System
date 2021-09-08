from django.core import paginator
from django.http.response import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from .models import Complaint, Tag, ComplaintTag, Reply
from django.contrib import messages
from django.http import HttpResponseRedirect
from common.utils import isValidInput, cleanInput
from common.decorators import loginRequired, logoutRequired, onlyAdmin, onlyUser, onlyPostRequest, notManager
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

User = get_user_model()

@loginRequired
@notManager
def index(request):
    user = request.user

    if user.isAdmin:
        complaintIDs = Reply.objects.filter(author = user).values_list("complaint").distinct()
        complaints = Complaint.objects.filter(id__in = complaintIDs)
        return render(request, "core/index.html", {
            "complaints": complaints,
        })
    else:
        if request.method == "POST":
            last = {}
            error = False
            title = request.POST.get("title")
            complaint = request.POST.get("complaint")
            tags = request.POST.getlist("tag")

            if isValidInput(title):
                title = cleanInput(title)
                last["title"] = title
            else:
                messages.error(request, "Invalid Title")
                error = True

            if isValidInput(complaint):
                complaint = cleanInput(complaint)
                last["complaint"] = complaint
            else:
                messages.error(request, "Invalid Complaint")
                error = True

            last["tag"] = []
            tagError = False

            for i in range(len(tags)):
                if isValidInput(tags[i]):
                    tags[i] = cleanInput(tags[i].lower())
                    last["tag"].append(tags[i].lower())
                else:                
                    tagError = True
                    error = True

            if tagError:
                messages.error(request, "Invalid Tag")

            if not error:
                complaint = Complaint.objects.create(
                    title = title,
                    complaint = complaint,
                    author = user
                )
                
                for tag in set(tags):
                    tagObject, created = Tag.objects.get_or_create(name = tag)
                    ComplaintTag.objects.create(
                        complaint = complaint,
                        tag = tagObject
                    )
            
                messages.success(request, "Complaint added successfully!")
            else:
                return render(request, "core/index.html", {
                    "complaints": Complaint.objects.filter(author = user),
                    "last": last
                })

        return render(request, "core/index.html", {
            "complaints": Complaint.objects.filter(author = user),
        })

@logoutRequired
def register(request):
    if request.method == "POST":
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName", "")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmPassword")
        error = False
        last = {}

        if isValidInput(firstName):
            firstName = cleanInput(firstName)
            last["firstName"] = firstName
        else:
            messages.error(request, "Invalid First Name")
            error = True

        lastName = cleanInput(lastName)
        last["lastName"] = lastName

        if isValidInput(email):
            email = cleanInput(email)
            last["email"] = email
        else:
            messages.error(request, "Invalid Email")
            error = True

        if isValidInput(password):
            password = cleanInput(password)
        else:
            messages.error(request, "Invalid Password")
            error = True

        if isValidInput(confirmPassword):
            confirmPassword = cleanInput(confirmPassword)
        else:
            messages.error(request, "Invalid Confirm Password")
            error = True

        if password != confirmPassword:
            messages.error(request, "Passwords don't match")
            error = True

        if not error:
            user = User(
                email = email,
                firstName = firstName,
                lastName = lastName
            )
            user.set_password(password)
            user.save()
            messages.success(request, f"Hi {firstName}, your account has been created successfully!")
            return HttpResponseRedirect("/login/")
        else:
            return render(request, "core/register.html", {
                "last": last
            })

    return render(request, "core/register.html", {})

@loginRequired
def editAccount(request):
    user = request.user

    if request.method == "POST":
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName", "")

        if isValidInput(firstName):
            firstName = cleanInput(firstName)
        else:
            messages.error(request, "Invalid First Name")
            firstName = user.firstName

        lastName = cleanInput(lastName)
        user.firstName = firstName
        user.lastName = lastName
        user.save()
        messages.success(request, f"Changes saved successfully!")

    return render(request, "core/edit-account.html", {
        "user": user
    })

@logoutRequired
def loginView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(
            email = email,
            password = password
        )

        if user == None or user.isManager:
            messages.error(request, "Invalid Credentials.")
            return render(request, "core/login.html", {})        
        
        login(request, user)
        messages.success(request, f"You have been logged in successfully!")
        return HttpResponseRedirect("/")

    return render(request, "core/login.html", {})

@loginRequired
@notManager
def logoutView(request):
    logout(request)
    messages.success(request, f"You have been logged out successfully!")
    return HttpResponseRedirect("/")

@loginRequired
@onlyAdmin
def complaints(request):
    query = request.GET.get("query", "")
    all = request.GET.get("all") == "on"

    if isValidInput(query):
        cIDs = ComplaintTag.objects.filter(
            Q(tag__name__icontains = query) |
            Q(complaint__title__icontains = query)
        ).values_list("complaint__id").distinct()

        if all:
            complaints = Complaint.objects.filter(id__in = cIDs)
        else:
            complaints = Complaint.objects.filter(status = False).filter(id__in = cIDs)
    else:
        if all:
            complaints = Complaint.objects.all()    
        else:
            complaints = Complaint.objects.filter(status = False)    

    page = request.GET.get("page", 1)
    paginator = Paginator(complaints, 20)

    try:
        complaints = paginator.page(page)
    except PageNotAnInteger:
        complaints = paginator.page(1)
    except EmptyPage:
        complaints = paginator.page(paginator.num_pages)

    return render(request, "core/complaints.html", {
        "complaints": complaints,
        "all": all,
        "query": query
    })

@loginRequired
@onlyAdmin
@onlyPostRequest
def resolved(request, slug):
    complaint = Complaint.objects.filter(slug = slug)

    if complaint.exists():
        complaint = complaint.first()
        complaint.status = True
        complaint.save()
        return HttpResponseRedirect(f"/complaint/{slug}/")
    else:
        return HttpResponseRedirect("/")

@loginRequired
@onlyPostRequest
def unresolved(request, slug):
    user = request.user
    complaint = Complaint.objects.filter(slug = slug)

    if complaint.exists() and (user.isAdmin or complaint.first().author == user):
        complaint = complaint.first()
        complaint.status = False
        complaint.save()
        return HttpResponseRedirect(f"/complaint/{slug}/")
    else:
        return HttpResponseRedirect("/")

@loginRequired
@notManager
def viewComplaint(request, slug):
    user = request.user
    complaint = Complaint.objects.filter(slug = slug)

    if complaint.exists():
        complaint = complaint.first()

        if request.method == "POST" and (user.isAdmin or user == complaint.author):
            reply = request.POST.get("reply")
            Reply.objects.create(
                reply = reply,
                author = user,
                complaint = complaint,
            )

        return render(request, "core/complaint.html", {
            "complaint": complaint,
            "replies": Reply.objects.filter(complaint = complaint).order_by("dateCreated"),
            "today": timezone.now()
        })
    else:
        messages.error(request, "Complaint doesn't exists.")
        return HttpResponseRedirect("/")

@loginRequired
@onlyUser
def editComplaint(request, slug):
    complaint = Complaint.objects.filter(
        author = request.user,
        slug = slug
    )

    if not complaint.exists():
        messages.error(request, "Complaint doesn't exists.")
        return HttpResponseRedirect("/")

    complaint = complaint.first()

    if request.method == "POST":
        title = request.POST.get("title")
        complaintText = request.POST.get("complaint")
        tags = request.POST.getlist("tag")

        if isValidInput(title):
            title = cleanInput(title)
        else:
            title = complaint.title
            messages.error(request, "Invalid Title")

        if isValidInput(complaintText):
            complaintText = cleanInput(complaintText)
        else:
            messages.error(request, "Invalid Complaint")
            complaintText = complaint.complaint

        tagError = False
        complaint.tags.all().delete()

        for i in range(len(tags)):
            if isValidInput(tags[i]):
                tags[i] = cleanInput(tags[i]).lower()
            else:                
                tagError = True

        if tagError:
            messages.error(request, "Invalid Tag")

        complaint.title = title
        complaint.complaint = complaintText
        complaint.save()
        
        for tag in set(tags):
            tagObject, created = Tag.objects.get_or_create(name = tag)
            ComplaintTag.objects.create(
                complaint = complaint,
                tag = tagObject
            )

        messages.success(request, "Complaint saved successfully!")

    return render(request, "core/edit-complaint.html", {
        "complaint": complaint
    })
        
@loginRequired
@onlyUser
def deleteComplaint(request, slug):
    complaint = Complaint.objects.filter(
        author = request.user,
        slug = slug
    )

    if complaint.exists():
        complaint.first().delete()
        messages.success(request, "Complaint deleted successfully!")
    else:
        messages.error(request, "Complaint doesn't exists or belongs to you.")
    
    return HttpResponseRedirect("/")