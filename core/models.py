import random
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, firstName, password = None):
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(
            email = self.normalize_email(email),
            firstName = firstName
        )

        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, firstName, password):
        user = self.create_user(
            email = self.normalize_email(email),
            firstName = firstName,
            password = password
        )

        user.isAdmin = True
        user.isSuperuser = True
        user.save(using = self._db)
        return user

def generateUserSlug():
    length = 100
    domain = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    while True:
        slug = "".join(random.choices(domain, k = length))

        if not User.objects.filter(slug = slug).exists():
            return slug

class User(AbstractBaseUser):
    email = models.EmailField(max_length = 200, unique = True)
    firstName = models.CharField(max_length = 100)
    lastName = models.CharField(max_length = 100, blank = True)
    dateJoined = models.DateTimeField(verbose_name = "Date of Joining", auto_now_add = True)
    dateLastLogin = models.DateTimeField(verbose_name = "Date of Last Login", auto_now = True)
    active = models.BooleanField(default = True)
    isSuperuser = models.BooleanField(default = False)
    isAdmin = models.BooleanField(default = False)
    isManager = models.BooleanField(default = False)
    slug = models.SlugField(max_length = 100, unique = True, default = generateUserSlug)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstName"]

    objects = UserManager()

    class Meta:
        db_table = "User"

    @property
    def is_staff(self):
        return self.isSuperuser

    @property
    def is_superuser(self):
        return self.isSuperuser

    @property
    def is_admin(self):
        return self.isAdmin

    @property
    def isAuthenticated(self):
        return self.is_authenticated

    @property
    def isAnonymous(self):
        return self.is_anonymous

    def __str__(self):
        return f"{self.email} | {self.getName()}"

    def has_perm(self, perm, obj = None):
        return self.isSuperuser

    def has_module_perms(self, app_label):
        return True

    def getName(self):
        return " ".join([self.firstName, self.lastName])

class ManagerAdmin(models.Model):
    manager = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "admins")
    admin = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "manager")

    class Meta:
        verbose_name = "ManagerAdmin"
        verbose_name_plural = "ManagerAdmins"

def generateComplaintSlug():
    length = 100
    domain = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    while True:
        slug = "".join(random.choices(domain, k = length))

        if not Complaint.objects.filter(slug = slug).exists():
            return slug

class Complaint(models.Model):
    title = models.CharField(max_length = 500)
    complaint = models.TextField()
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "complaints")
    status = models.BooleanField(default = False)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    slug = models.SlugField(max_length = 100, unique = True, default = generateComplaintSlug)

    class Meta:
        db_table = "complaints"

class Tag(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.CharField(max_length = 200)
    dateCreated = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)
    
    class Meta:
        db_table = "tags"

class ComplaintTag(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete = models.CASCADE, related_name = "tags")
    tag = models.ForeignKey(Tag, on_delete = models.CASCADE, related_name = "complaints")
    dateCreated = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        db_table = "complaint_tags"
        verbose_name = "ComplaintTag"
        verbose_name_plural = "ComplaintTags"

class Reply(models.Model):
    reply = models.TextField()
    complaint = models.ForeignKey(Complaint, on_delete = models.CASCADE, related_name = "replies")
    author = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, related_name = "replies")
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    
    class Meta:
        db_table = "replies"