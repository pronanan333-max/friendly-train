from django.urls import path
from . import views
from . import account


urlpatterns = [
    path('', views.home, name="home"),
    path('profile_list/', views.profile_list, name='profile_list'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/followers/<int:pk>', views.followers, name='followers'),
    path('profile/follows/<int:pk>', views.follows, name='follows'),
    
    path('login/', account.login_user, name='login'),
    path('logout', account.logout_user, name='logout'),
    path('register/', account.register_user, name='register'),
    path('activate/<uidb64>/<token>/', account.activate, name='activate'),
    path('update_user/', views.update_user, name='update_user'),
    path('meep_like/<int:pk>', views.meep_like, name="meep_like"),
    path('meep_show/<int:pk>', views.meep_show, name="meep_show"),
    path('unfollow/<int:pk>', views.unfollow, name="unfollow"),
    path('follow/<int:pk>', views.follow, name="follow"),
    path('delete_meep/<int:pk>', views.delete_meep, name="delete_meep"),
    path('edit_meep/<int:pk>', views.edit_meep, name="edit_meep"),
    path('search/', views.search, name='search'),
    path('donate/', views.donate_view, name='donate'),
    path("donate/success/", views.donate_success, name="donate_success"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),


]
