from django.contrib import messages
from django.contrib.auth import get_user_model
from common.utils import isValidInput, cleanInput
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from common.decorators import logoutRequired, onlyManager

User = get_user_model()

@logoutRequired
def loginView(request):
	if request.method == "POST":
		email = request.POST.get("email")
		password = request.POST.get("password")
		user = authenticate(
			email = email,
			password = password
		)

		print(user)
		if user == None or not user.isManager:
			messages.error(request, "Invalid Credentials.")
			return render(request, "managers/login.html", {})

		login(request, user)
		messages.success(request, f"You have been logged in successfully!")
		return HttpResponseRedirect("/managers/dashboard/")

	return render(request, "managers/login.html", {})

@login_required(login_url = "/managers/login/")
@onlyManager
def logoutView(request):
	logout(request)
	messages.success(request, f"You have been logged out successfully!")
	return HttpResponseRedirect("/managers/login/")

@login_required(login_url = "/managers/login/")
@onlyManager
def dashboard(request):
	manager = request.user
	admins = User.objects.filter(isAdmin = True)

	return render(request, "managers/manager-dashboard.html", {
		"manager": manager,
		"admins": admins,
	})

@login_required(login_url = "/managers/login/")
@onlyManager
def newAdmin(request):
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
			messages.success(request, f"New admin has been created successfully!")
			return HttpResponseRedirect("/manager/dashboard")

		return render(request, "managers/new-admin.html", {
			"last": last
		})

	return render(request, "managers/new-user.html", {})

@login_required(login_url = "/managers/login/")
@onlyManager
def removeAdmin(request):
	if request.method == "POST":
		email = request.POST.get("email")
		user = User.objects.filter(email = email)

		if not user.exists():
			messages.error(request, "No such admin exists.")
			return HttpResponseRedirect("/managers/dashboard/")	

		user = user.first()
		user.delete()
		messages.success(request, "Admin removed successfully!")	
		
	return HttpResponseRedirect("/managers/dashboard/")	 

@login_required(login_url = "/managers/login/")
@onlyManager
def editAdmin(request, slug):
	user = User.objects.filter(slug = slug)

	if not user.exists():
		messages.error(request, "No such admin exists.")
		return HttpResponseRedirect("/managers/dashboard/")	
	
	user = user.first()

	if request.method == "POST":
		firstName = request.POST.get("firstName").strip()
		
		if isValidInput(firstName):
			firstName = cleanInput(firstName)
		else:
			messages.error(request, "Invalid First Name")

		lastName = request.POST.get("lastName").strip()
		user.firstName = firstName
		user.lastName = lastName
		user.save()
		messages.success(request, "Changes saved successfully!")

	return render(request, "managers/edit-recruiter.html", {
		"admin": user,
	})