
from django.urls import path
from .views import (Home,Index,Register,Charts,Search,Tables,AddMoneySubmission,Check,Weekly,ExpenseWeek,Stats,ExpenseMonth,ExpenseEdit,
                    Password,AddMoney,Profile,ProfileEdit,ProfileUpdateView,HandleLogin,AddMoneyUpdate,
                    HandleLogout,HandleSignUp,Info,InfoYear,ExpenseDelete,ExpenseDelete)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('index/', Index.as_view(), name='index'),
    path('register/',Register.as_view(),name='register'),
    path('handleSignup/',HandleSignUp.as_view(),name='handleSignup'),
    path('handlelogin/',HandleLogin.as_view(),name='handlelogin'),
    path('handleLogout/',HandleLogout.as_view(),name='handleLogout'),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name = "home/reset_password.html"),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="home/reset_password_sent.html"),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name ="home/password_reset_form.html"),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetView.as_view(template_name ="home/password_reset_done.html"),name='password_reset_complete'),
    path('addmoney/',AddMoney.as_view(),name='addmoney'),
    path('addmoney_submission/',AddMoneySubmission.as_view(),name='addmoney_submission'),
    path('charts/',Charts.as_view(),name='charts'),
    path('tables/',Tables.as_view(),name='tables'),
    path('expense_edit/<int:id>',ExpenseEdit.as_view(),name='expense_edit'),
    path('<int:id>/addmoney_update/', AddMoneyUpdate.as_view(), name="addmoney_update") ,
    path('expense_delete/<int:id>',ExpenseDelete.as_view(),name='expense_delete'),
    path('profile/',Profile.as_view(),name = 'profile'),
    path('expense_month/',ExpenseMonth.as_view(), name = 'expense_month'),
    path('stats/',Stats.as_view(), name = 'stats'),
    path('expense_week/',ExpenseWeek.as_view(), name = 'expense_week'),
    path('weekly/',Weekly.as_view(), name = 'weekly'),
    path('check/',Check.as_view(),name="check"),
    path('search/',Search.as_view(),name="search"),
    path('<int:id>/profile_edit/',ProfileEdit.as_view(),name="profile_edit"),
    path('<int:id>/profile_update/',ProfileUpdateView.as_view(),name="profile_update"),
    path('info/',Info.as_view(),name="info"),
    path('info_year/',InfoYear.as_view(),name="info_year"),
]
