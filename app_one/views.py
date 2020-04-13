from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Category, App, UserApp, Image, Background, Tutorial
import bcrypt

#RENDER Views:
def index(request):
    context = {

    }
    return render(request, 'index.html', context)


def dashboard(request):
    if 'userid' not in request.session:
        return redirect('/')

    # userback = User.objects.get(id=request.session['userid'])
    # if userback.background == None:
    #     userback.background = Background.objects.get(id=1)
    #     userback.save()

    appscats = UserApp.objects.filter(user=User.objects.get(id=request.session['userid'])).order_by('-app__name')
    
    ## Parse and sort user categories
    nocat = False
    usercats = {}
    sortedcats = []
    for user in appscats:
        if user.category == None:
            nocat = True
        if user.category not in usercats:
            usercats[user.category] = user.category
    for cat in usercats:
        if cat != None:
            sortedcats.append(cat.name)
    sortedcats.sort()

    complete_tuts = {}
    for tutorial in User.objects.get(id=request.session['userid']).tutorials.all():
        if tutorial.name not in complete_tuts:
            pass
    
    intro_tut_done = False
    if len(User.objects.get(id=request.session['userid']).tutorials.filter(name="Intro")) == 0:
        intro_tut_done = True

    context = {
        'backgrounds': Background.objects.all().order_by('name'),
        'user': User.objects.get(id=request.session['userid']),
        'apps': User.objects.get(id=request.session['userid']).apps.all(),
        'usercats': sortedcats,
        'appscats': appscats,
        'nocat': nocat,
        'images': Image.objects.all(),
        'intro_tut': Tutorial.objects.first(),
        'tutorials': Tutorial.objects.all(),
        'intro_tut_done': intro_tut_done,
    }
    return render(request, 'dashboard.html', context)




## REGISTRATION/LOGIN/LOGOUT Views:
def register(request):
    errors = User.objects.reg_validator(request.POST)
    if len(errors) > 0:
        print("In errors")
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/')
    else:
        ("in account created")
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        User.objects.create (
            first_name= request.POST['first_name'],
            last_name= request.POST['last_name'],
            email= request.POST['email'],
            password= pw_hash,
        )
        user = User.objects.last()
        request.session['userid'] = user.id
        return redirect('/dashboard')


def login(request):
    errors = User.objects.log_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/')
    else:
        user = User.objects.get(email=request.POST['email'])
        request.session['userid'] = user.id
        return redirect('/dashboard')


def logout(request):
    request.session.clear()
    return redirect('/')




## REDIRECT Views:
def add_app(request):
    if request.method == "POST":
        # errors = App.objects.app_validator(request.POST)
        # if len(errors) > 0:
        #     for key, value in errors.items():
        #         messages.error(request, value, extra_tags=key)
        #     return redirect('/dashboard')
        # else:
            print("****",request.POST['category'])
            if request.POST['category'] == "None":
                category = None
            elif len(Category.objects.filter(name=request.POST['category'])) == 0:
                category = Category.objects.create(
                    name=request.POST['category'],
                )
            else:
                category = Category.objects.get(name=request.POST['category'])

            if len(App.objects.filter(name=request.POST['app_name'])) == 0:
                App.objects.create(
                    name=request.POST['app_name'],
                )
            UserApp.objects.create(
                url=request.POST['url'],
                user=User.objects.get(id=request.session['userid']),
                category=category,
                app=App.objects.get(name=request.POST['app_name']),
                image=Image.objects.get(id=request.POST['image']),
            )
            App.objects.get(name=request.POST['app_name']).users.add(User.objects.get(id=request.session['userid']))
            if category != None:
                if len(App.objects.get(name=request.POST['app_name']).categories.filter(name=category.name)) == 0:
                    App.objects.get(name=request.POST['app_name']).categories.add(category)

            if 'intro_tut_active' in request.session:
                request.session['intro_tut_add_app'] = True

            return redirect('/dashboard')
            # return JsonResponse({'success':1})


def info_mode(request):
    if 'info_mode' not in request.session:
        request.session['info_mode'] = True
        return redirect('/dashboard')
    del request.session['info_mode']
    return redirect('/dashboard')


def edit_app(request):
    user = UserApp.objects.filter(user=User.objects.get(id=request.session['userid']), app=App.objects.get(id=request.POST['app_id']))[0]
    cat = UserApp.objects.filter(user=User.objects.get(id=request.session['userid']), app=App.objects.get(id=request.POST['app_id']))[0].category

    if request.POST['category'] == "None":
        category = None
    elif len(Category.objects.filter(name=request.POST['category'])) == 0:
        category = Category.objects.create(
            name=request.POST['category'],
        )
    else:
        category = Category.objects.get(name=request.POST['category'])
    
    user.url = request.POST['url']
    user.image = Image.objects.get(id=request.POST['image'])
    user.category = category
    user.save()

    if len(UserApp.objects.filter(app=App.objects.get(id=request.POST['app_id']),category=cat)) == 0:
        App.objects.get(id=request.POST['app_id']).categories.remove(cat)
    if cat != None:
        if len(UserApp.objects.filter(category=cat)) == 0:
            cat.delete()

    if category != None:
        if len(App.objects.get(id=request.POST['app_id']).categories.filter(name=category.name)) == 0:
            App.objects.get(id=request.POST['app_id']).categories.add(category)

    if 'intro_tut_add_app' in request.session:
        del request.session['intro_tut_add_app']
        request.session['intro_tut_edit_app'] = True

    return redirect('/dashboard')


# def delete_mode(request):
#     if 'delete_mode' not in request.session:
#         request.session['delete_mode'] = True
#         return redirect('/dashboard')
#     del request.session['delete_mode']
#     return redirect('/dashboard')


def delete_app(request, id):
    cat = UserApp.objects.filter(app=App.objects.get(id=id),user=User.objects.get(id=request.session['userid']))[0].category
    
    UserApp.objects.filter(app=App.objects.get(id=id),user=User.objects.get(id=request.session['userid']))[0].delete()
    
    App.objects.get(id=id).users.remove(User.objects.get(id=request.session['userid']))
    if len(UserApp.objects.filter(app=App.objects.get(id=id),category=cat)) == 0:
        App.objects.get(id=id).categories.remove(cat)
    if cat != None:
        if len(UserApp.objects.filter(category=cat)) == 0:
            cat.delete()
    if len(UserApp.objects.filter(app=App.objects.get(id=id))) == 0:
        App.objects.get(id=id).delete()

    return redirect('/dashboard')


# def new_app(request):
#     if 'new_app' not in request.session:
#         request.session['new_app'] = True
#         return redirect('/dashboard')
#     del request.session['new_app']
#     return redirect('/dashboard')


def change_bg(request, id):
    if id == 0:
        user = User.objects.get(id=request.session['userid'])
        user.background = None
        user.save()
    else:
        user = User.objects.get(id=request.session['userid'])
        user.background = Background.objects.get(id=id)
        user.save()
    return redirect('/dashboard')


def minimize_welcome(request):
    if 'min_welc' not in request.session:
        request.session['min_welc'] = True
        return redirect('/dashboard')
    del request.session['min_welc']
    return redirect('/dashboard')


def tutorial(request):
    user = User.objects.get(id=request.session['userid'])
    if user.tutorial_row == True:
        user.tutorial_row = False
    else:
        user.tutorial_row = True
    user.save()
    return redirect('/dashboard')


def intro_tut_complete(request):
    if 'intro_tut_active' in request.session:
        del request.session['intro_tut_active']
    if 'intro_tut_add_app' in request.session:
        del request.session['intro_tut_add_app']
    if 'intro_tut_edit_app' in request.session:
        del request.session['intro_tut_edit_app']
    request.session['final_tut'] = True
    User.objects.get(id=request.session['userid']).tutorials.add(Tutorial.objects.get(name="Intro"))
    return redirect('/dashboard')


def reset_intro_tut(request):
    User.objects.get(id=request.session['userid']).tutorials.remove(Tutorial.objects.get(name="Intro"))
    if 'final_tut' in request.session:
        del request.session['final_tut']
    return redirect('/dashboard')




## AJAX Views:
def ajax_reg_first_name(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
        return render(request, 'partials/reg_first_name.html')


def ajax_reg_last_name(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
        return render(request, 'partials/reg_last_name.html')


def ajax_reg_email(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return render(request, 'partials/reg_email.html')
        if errors['validem']:
            return render(request, 'partials/reg_email_valid.html')


def ajax_app_info(request, id):
    user = UserApp.objects.filter(user=User.objects.get(id=request.session['userid']),app=App.objects.get(id=id))[0]
    cats = user.app.categories.all().order_by('name')
    context = {
        'user': UserApp.objects.filter(user=User.objects.get(id=request.session['userid']),app=App.objects.get(id=id))[0],
        'cats': cats,
    }
    print(context['user'])
    return render(request, 'partials/app_info.html', context)


def ajax_edit_app(request, id):
    user = UserApp.objects.filter(user=User.objects.get(id=request.session['userid']),app=App.objects.get(id=id))[0]
    
    userapps = UserApp.objects.filter(user=User.objects.get(id=request.session['userid'])).order_by('category__name')
    usercats = {}
    for x in userapps:
        if x.category not in usercats:
            usercats[x.category] = x.category

    context = {
        'user': user,
        'images': Image.objects.all(),
        'usercats': usercats,
    }
    return render(request, 'partials/edit_app.html', context)


def ajax_new_app(request):
    user = User.objects.get(id=request.session['userid'])
    
    userapps = UserApp.objects.filter(user=User.objects.get(id=request.session['userid'])).order_by('category__name')
    usercats = {}
    for x in userapps:
        if x.category not in usercats:
            usercats[x.category] = x.category

    context = {
        'user': user,
        'images': Image.objects.all(),
        'usercats': usercats,
    }
    return render(request, 'partials/new_app.html', context)


def ajax_add_app_errors(request):
    if request.method == "POST":
        user = User.objects.get(id=request.session['userid'])
        
        userapps = UserApp.objects.filter(user=User.objects.get(id=request.session['userid'])).order_by('category__name')
        usercats = {}
        for x in userapps:
            if x.category not in usercats:
                usercats[x.category] = x.category

        context = {
            'user': user,
            'images': Image.objects.all(),
            'usercats': usercats,
        }
        errors = App.objects.app_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return render(request, 'partials/new_app.html', context)
        else:
            return JsonResponse({'success':1})


def ajax_activate_intro_tut(request):
    if 'intro_tut_active' not in request.session:
        request.session['intro_tut_active'] = True
    return redirect('/dashboard')


def ajax_close(request):
    return render(request, 'partials/empty.html')