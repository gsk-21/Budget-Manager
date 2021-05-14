from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-item', views.add_item, name='add-item'),
    path('remove-item', views.remove_item, name='remove-item'),
    path('monthly-budget', views.monthly_budget, name='monthly-budget'),
    path('single-month-budget/<int:month>,<int:year>',views.single_month_budget,name="single-month-budget"),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html',
                                                extra_context={'logged_in': 1}), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('set-theme',views.set_theme,name='set-theme')
]