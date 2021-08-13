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
        title = request.POST.get("title")
        complaint = request.POST.get("complaint")
        tags = request.POST.getlist("tag")
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

    return render(request, "core/index.html", {
        "complaints": Complaint.objects.filter(author = user)
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