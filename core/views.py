from django.shortcuts import render
from .models import Complaint, Tag, ComplaintTag
from django.contrib import messages
from django.http import HttpResponseRedirect
from common.utils import isValidInput, cleanInput
from common.decorators import loginRequired, logoutRequired, onlyUser
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

@loginRequired
@onlyUser
def index(request):
    user = request.user

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
                tags[i] = cleanInput(tags[i])
                last["tag"].append(tags[i])
            else:                
                tagError = True
                error = True

        if tagError:
            print("Hello")
            messages.error(request, "Invalid Tag")

        if not error:
            complaint = Complaint.objects.create(
                title = title,
                complaint = complaint,
                author = user
            )
            
            for tag in tags:
                tagObject = Tag.objects.create(name = tag)
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

@logoutRequired
def loginView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(
            email = email,
            password = password
        )

        if user == None:
            messages.error(request, "Invalid Credentials.")
            return render(request, "core/login.html", {})        
        else:
            login(request, user)
            messages.success(request, f"You have been logged in successfully!")
            return HttpResponseRedirect("/")

    return render(request, "core/login.html", {})

@loginRequired
def logoutView(request):
    logout(request)
    messages.success(request, f"You have been logged out successfully!")
    return HttpResponseRedirect("/")

@loginRequired
def viewComplaint(request, slug):
    complaint = Complaint.objects.filter(slug = slug)

    if complaint.exists():
        return render(request, "core/complaint.html", {
            "complaint": complaint.first()
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
        complaint = request.POST.get("complaint")
        tags = request.POST.getlist("tag")
        complaint.title = title
        complaint.complaint = complaint
        complaint.save()
        ComplaintTag.objects.filter(complaint = complaint).delete()

        for tag in tags:
            tagObject = Tag.objects.create(name = tag)
            ComplaintTag.objects.create(
                complaint = complaint,
                tag = tagObject
            )

        messages.success(request, "Complaint saved successfully!")

    return render(request, "edit-complaint.html", {
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