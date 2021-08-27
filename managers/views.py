from django.contrib import messages
from django.contrib.auth import get_user_model
from common.utils import isValidInput, cleanInput
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from common.decorators import logoutRequired, onlyManager
from core.models import ManagerAdmin

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
	admins = [admin.admin for admin in manager.admins.all().order_by("admin__firstName")]
	counts = []

	for admin in admins:
		complaints = list(set([a.complaint for a in admin.replies.all()]))
		resolved, resolving = 0, 0

		for c in complaints:
			if c.status:
				resolved += 1
			else:
				resolving += 1

		counts.append({"resolved" : resolved, "resolving" : resolving})

	return render(request, "managers/manager-dashboard.html", {
		"manager": manager,
		"admins": zip(admins, counts)
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

			if User.objects.filter(email = email).exists():
				messages.error(request, "Email already exists.")	
				last["email"] = email
				return render(request, "managers/new-admin.html", {
					"last": last
				})
			
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
			manager = request.user
			ManagerAdmin.objects.create(admin = user, manager = manager)
			messages.success(request, f"New admin has been created successfully!")
			return HttpResponseRedirect("/managers/dashboard")

		return render(request, "managers/new-admin.html", {
			"last": last
		})

	return render(request, "managers/new-admin.html", {})

@login_required(login_url = "/managers/login/")
@onlyManager
def removeAdmin(request):
	if request.method == "POST":
		slug = request.POST.get("slug")

		if slug == None:
			messages.error(request, "Invalid URL.")
			return HttpResponseRedirect("/managers/dashboard/")

		manager = request.user
		user = User.objects.filter(slug = slug)

		if not user.exists():
			messages.error(request, "No such admin exists.")
			return HttpResponseRedirect("/managers/dashboard/")

		user = user.first()

		if not ManagerAdmin.objects.filter(admin = user, manager = manager).exists():
			messages.error(request, "Admin was not created by you.")
			return HttpResponseRedirect("/managers/dashboard/")

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
			firstName = user.firstName
			messages.error(request, "Invalid First Name")

		lastName = request.POST.get("lastName").strip()
		user.firstName = firstName
		user.lastName = lastName
		user.save()
		messages.success(request, "Changes saved successfully!")

	return render(request, "managers/edit-admin.html", {
		"user": user,
	})