from django.urls import path
from . import views

urlpatterns = [
    ## RENDER 
    path('', views.index),
    path('dashboard', views.dashboard),


    ## REGISTRATION/LOGIN/LOGOUT
    path('rd/reg', views.register),
    path('rd/login', views.login),
    path('rd/logout', views.logout),


    ## REDIRECT
    path('rd/add_app', views.add_app),
    path('rd/info_mode', views.info_mode),
    path('rd/edit_app', views.edit_app),
    # path('rd/delete_mode', views.delete_mode),
    path('rd/delete_app/<int:id>', views.delete_app),
    # path('rd/new_app', views.new_app),
    path('rd/change_bg/<int:id>', views.change_bg),
    path('rd/minimize_welcome', views.minimize_welcome),

    path('rd/tutorial', views.tutorial),
    path('rd/intro_tut_complete', views.intro_tut_complete),
    path('rd/reset_intro_tut', views.reset_intro_tut),


    ## AJAX CALLS
    path('ajax_reg_first_name', views.ajax_reg_first_name),
    path('ajax_reg_last_name', views.ajax_reg_last_name),
    path('ajax_reg_email', views.ajax_reg_email),

    path('ajax_app_info/<int:id>', views.ajax_app_info),
    path('ajax_edit_app/<int:id>', views.ajax_edit_app),
    path('ajax_new_app', views.ajax_new_app),
    path('ajax_add_app_errors', views.ajax_add_app_errors),
    path('ajax_activate_intro_tut', views.ajax_activate_intro_tut),
    path('ajax_close', views.ajax_close),
]