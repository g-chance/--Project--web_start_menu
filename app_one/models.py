from django.db import models
from django.core.validators import URLValidator
import re
import bcrypt

#Managers
class UserManager(models.Manager):
    def reg_validator(self, post):
        errors = {}
        if len(post['first_name']) < 2:
            errors['first_name'] = "Your first name must be at least 2 characters"
        if len(post['last_name']) < 2:
            errors['last_name'] = "Your last name must be at least 2 characters"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post['email']):
            errors['email'] = "Invalid Email address"
        if len(post['email']) == 0:
            errors['email'] = "Must enter an email address"
        if len(User.objects.filter(email=post['email'])) > 0:
            errors['email'] = "Email already taken"
        if len(post['password']) < 8:
            errors['reg_pw'] = "Your password should be at least 8 characters"
        if post['password'] != post['confirm_password']:
            errors['confirm_pw'] = "Passwords do not match"
        return errors
    
    def log_validator(self, post):
        errors = {}
        if len(User.objects.filter(email=post['email'])) == 0:
            errors['login_em'] = "Invalid email"
        else:
            user = User.objects.get(email=post['email'])
            if not bcrypt.checkpw(post['password'].encode(), user.password.encode()):
                errors['login_pw'] = "Incorrect email/password combination"
        return errors

class CategoryManager(models.Manager):
    def cat_validator(self, post):
        pass

class AppManager(models.Manager):
    def app_validator(self, post):
        errors = {}
        if len(post['app_name']) < 1:
            errors['app_name'] = "App name must be at least 1 character"
        if len(App.objects.filter(name=post['app_name'])) > 0:
            if len(App.objects.get(name=post['app_name']).users.filter(id=post['userid'])) > 0:
                errors['app_name'] = "App already added to Dashboard"
        # try:
        #     URLValidator()(post['url'])
        #     pass
        # except:
        #     errors['url'] = "Invalid URL"
        return errors


#Models
class Background(models.Model):
    name = models.CharField(max_length=255, null=True)
    link = models.TextField(null = True)
### users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    tutorial_row = models.BooleanField(default=True)
    background = models.ForeignKey(Background, related_name='users', null=True, on_delete=models.CASCADE)
        ### categories
### apps
### appscats
### tutorials
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Tutorial(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="tutorials")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    name = models.CharField(max_length=255)
        # users = models.ManyToManyField(User, related_name='categories')
### apps
### userapps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Image(models.Model):
    name = models.CharField(max_length=255, null=True)
    link = models.TextField(null = True)
### userapps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class App(models.Model):
    name = models.CharField(max_length=255)
    # url = models.URLField()
    image = models.CharField(max_length=255, null=True)
    tutorial = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='apps')
    categories = models.ManyToManyField(Category, related_name='apps')
### appscats
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AppManager()

class UserApp(models.Model):
    url = models.URLField(null=True)
    user = models.ForeignKey(User, related_name='appscats', on_delete=models.CASCADE)
    app = models.ForeignKey(App, related_name='userscats', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='usersapps', null=True, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, related_name='userapps', null = True, on_delete=models.CASCADE)