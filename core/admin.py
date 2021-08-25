from django.contrib import admin
from .models import User, Complaint, Tag, ComplaintTag, Reply

admin.site.register(User)
admin.site.register(Complaint)
admin.site.register(Tag)
admin.site.register(ComplaintTag)
admin.site.register(Reply)