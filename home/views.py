from django.shortcuts import get_object_or_404, render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Addmoney_info,UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone


# Create your views here.

class Home(View):
    def get(self,request,*args,**kwargs):
        if request.session.has_key('is_logged'):
            return redirect('/index')
        return render(request,'home/login.html')
    # return HttpResponse('This is home')


class Index(View):
    def get(self,request,*args,**kwargs):
        if request.session.has_key('is_logged'):
            user_id = request.session["user_id"]
            user = User.objects.get(id=user_id)
            addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
            paginator = Paginator(addmoney_info , 4)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator,page_number)
            context = {
                'add_info' : addmoney_info,
                'page_obj' : page_obj,
            }
        #if request.session.has_key('is_logged'):
            return render(request,'home/index.html',context)
        return redirect('home')
    #return HttpResponse('This is blog')


class Register(View):
    def get(self,request,*args,**kwargs):
        return render(request,'home/register.html')
        #return HttpResponse('This is blog')

class Password(View):
    def get(self,request,*args,**kwargs):
        return render(request,'home/password.html')


class Charts(View):
    def get(self,request,*args,**kwargs):
        return render(request,'home/charts.html')

class Search(View):
    def get(self,request,*args,**kwargs):
        if request.session.has_key('is_logged'):
            user_id = request.session["user_id"]
            user = User.objects.get(id=user_id)
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']
            addmoney = Addmoney_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
            return render(request,'home/tables.html',{'addmoney':addmoney})
        return redirect('home')

class Tables(View,LoginRequiredMixin,UserPassesTestMixin):
    def post(self,request,*args,**kwargs):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addmoney_info.objects.filter(user=user).order_by('-Date')
        return render(request, 'home/tables.html', {'addmoney': addmoney})

    def get(self,request,*args,**kwargs):
        return redirect('home')
    

class AddMoney(View,LoginRequiredMixin,UserPassesTestMixin):
    def get(self,request,*args,**kwargs):
        return render(request,'home/addmoney.html')

class Profile(View,LoginRequiredMixin,UserPassesTestMixin):
    def get(self,request,*args,**kwargs):
        if request.session.has_key('is_logged'):
            return render(request,'home/profile.html')
        return redirect('/home')


class ProfileEdit(View,LoginRequiredMixin,UserPassesTestMixin):
    def post(request,id):
        if request.session.has_key('is_logged'):
            user = User.objects.get(id=id)
            # user_id = request.session["user_id"]
            # user1 = User.objects.get(id=user_id)
            return render(request,'home/profile_edit.html',{'user':user})
        return redirect("/home")

class ProfileUpdateView(View,LoginRequiredMixin,UserPassesTestMixin):
    def post(self,request,id,*args,**kwargs):
        if request.session.has_key('is_logged'):
            if request.method == "POST":
                user = User.objects.get(id=id)
                user.first_name = request.POST["fname"]
                user.last_name = request.POST["lname"]
                user.email = request.POST["email"]
                user.userprofile.Savings = request.POST["Savings"]
                user.userprofile.income = request.POST["income"]
                user.userprofile.profession = request.POST["profession"]
                user.userprofile.save()
                user.save()
                return redirect("/profile")
            return redirect("/home")   

class HandleSignUp(View):
    def post(self, request):
        # Get the post parameters
        uname = request.POST["uname"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        profession = request.POST['profession']
        Savings = request.POST['Savings']
        income = request.POST['income']
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        # Check for errors in input
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken, Try something else!!!")
            return redirect("/register")

        if len(uname) > 15:
            messages.error(request, "Username must be max 15 characters, Please try again")
            return redirect("/register")

        if not uname.isalnum():
            messages.error(request, "Username should only contain letters and numbers, Please try again")
            return redirect("/register")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match, Please try again")
            return redirect("/register")

        # Create the user
        user = User.objects.create_user(uname, email, pass1)
        user.first_name = fname
        user.last_name = lname
        user.save()

        # Create the user profile
        profile = UserProfile(user=user, Savings=Savings, profession=profession, income=income)
        profile.save()

        messages.success(request, "Your account has been successfully created")
        return redirect("/")

    def get(self, request):
        return HttpResponse('404 - NOT FOUND')

class HandleLogin(View):
    def post(self, request):
        # Get the post parameters
        loginuname = request.POST["loginuname"]
        loginpassword1 = request.POST["loginpassword1"]
        user = authenticate(username=loginuname, password=loginpassword1)
        
        if user is not None:
            dj_login(request, user)
            request.session['is_logged'] = True
            request.session["user_id"] = user.id
            messages.success(request, "Successfully logged in")
            return redirect('/index')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect("/")
    
    def get(self, request):
        return HttpResponse('404 - NOT FOUND')
    

class HandleLogout(View):    
    def get(self,request):
            del request.session['is_logged']
            del request.session["user_id"] 
            logout(request)
            messages.success(request, " Successfully logged out")
            return redirect('home')

#add money form
class AddMoneySubmission(View):
    def post(self, request):
        if request.session.has_key('is_logged'):
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')

            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            Date = request.POST["Date"]
            Category = request.POST["Category"]

            add = Addmoney_info(user=user1, add_money=add_money, quantity=quantity, Date=Date, Category=Category)
            add.save()

            paginator = Paginator(addmoney_info1, 4)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'page_obj': page_obj
            }
            return render(request, 'home/index.html', context)

        return redirect('/index')

    def get(self, request):
        return redirect('/index')
    

class AddMoneyUpdate(View):
    def post(self, request, id):
        if request.session.has_key('is_logged'):
            add = get_object_or_404(Addmoney_info, id=id)
            add.add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add.save()
            return redirect("/index")
        return redirect("/home")

    def get(self, request, id):
        if request.session.has_key('is_logged'):
            add = get_object_or_404(Addmoney_info, id=id)
            context = {
                'add': add
            }
            return render(request, 'home/update.html', context)
        return redirect("/home")       

class ExpenseEdit(View):
    def get(self, request, id):
        if request.session.has_key('is_logged'):
            addmoney_info = get_object_or_404(Addmoney_info, id=id)
            user_id = request.session["user_id"]
            user1 = get_object_or_404(User, id=user_id)
            context = {'addmoney_info': addmoney_info}
            return render(request, 'home/expense_edit.html', context)
        return redirect("/home")  

class ExpenseDelete(View):
    def get(self,request,id):
        if request.session.has_key('is_logged'):
            addmoney_info = Addmoney_info.objects.get(id=id)
            addmoney_info.delete()
            return redirect("/index")
        return redirect("/home")  

class ExpenseMonth(View):
    def get(self, request):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney = Addmoney_info.objects.filter(user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
        finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category

        Category_list = list(set(map(get_Category, addmoney)))

        def get_expense_category_amount(Category):
            quantity = 0
            filtered_by_category = addmoney.filter(Category=Category, add_money="Expense")
            for item in filtered_by_category:
                quantity += item.quantity
            return quantity

        for y in Category_list:
            finalrep[y] = get_expense_category_amount(y)

        return JsonResponse({'expense_category_data': finalrep}, safe=False)
    

class Stats(View):
    def get(self, request):
        if request.session.has_key('is_logged'):
            todays_date = datetime.date.today()
            one_month_ago = todays_date - datetime.timedelta(days=30)
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            addmoney_info = Addmoney_info.objects.filter(user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
            sum_expenses = sum(i.quantity for i in addmoney_info if i.add_money == 'Expense')
            sum_income = sum(i.quantity for i in addmoney_info if i.add_money == 'Income')

            user1.userprofile.Savings += sum_income - sum_expenses
            x = user1.userprofile.Savings
            y = max(0, -x)

            if x < 0:
                messages.warning(request, 'Your expenses exceeded your savings')
                x = 0

            context = {'addmoney_info': addmoney_info, 'sum': sum_expenses, 'sum1': sum_income, 'x': abs(x), 'y': abs(y)}
            return render(request, 'home/stats.html', context)
        return redirect('/home')

class ExpenseWeek(View):
    def get(self, request):
        todays_date = datetime.date.today()
        one_week_ago = todays_date - datetime.timedelta(days=7)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney = Addmoney_info.objects.filter(user=user1, Date__gte=one_week_ago, Date__lte=todays_date)
        finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category

        Category_list = list(set(map(get_Category, addmoney)))

        def get_expense_category_amount(Category):
            quantity = 0
            filtered_by_category = addmoney.filter(Category=Category, add_money="Expense")
            for item in filtered_by_category:
                quantity += item.quantity
            return quantity

        for y in Category_list:
            finalrep[y] = get_expense_category_amount(y)

        return JsonResponse({'expense_category_data': finalrep}, safe=False)
    
class Weekly(View):
    def get(self, request):
        if request.session.has_key('is_logged'):
            todays_date = datetime.date.today()
            one_week_ago = todays_date - datetime.timedelta(days=7)
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            addmoney_info = Addmoney_info.objects.filter(user=user1, Date__gte=one_week_ago, Date__lte=todays_date)
            sum_expenses = sum(i.quantity for i in addmoney_info if i.add_money == 'Expense')
            sum_income = sum(i.quantity for i in addmoney_info if i.add_money == 'Income')

            user1.userprofile.Savings += sum_income - sum_expenses
            x = user1.userprofile.Savings
            y = max(0, -x)

            if x < 0:
                messages.warning(request, 'Your expenses exceeded your savings')
                x = 0

            context = {'addmoney_info': addmoney_info, 'sum': sum_expenses, 'sum1': sum_income, 'x': abs(x), 'y': abs(y)}
            return render(request, 'home/weekly.html', context)
        return redirect('/home')

class Check(View):
    def post(self, request):
        if not User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "Email not registered, TRY AGAIN!!!")
            return redirect("/reset_password")
        return redirect("/")

class InfoYear(View):
    def get(self, request):
        todays_date = datetime.date.today()
        one_year_ago = todays_date - datetime.timedelta(days=30*12)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney = Addmoney_info.objects.filter(user=user1, Date__gte=one_year_ago, Date__lte=todays_date)
        finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category

        Category_list = list(set(map(get_Category, addmoney)))

        def get_expense_category_amount(Category):
            quantity = 0
            filtered_by_category = addmoney.filter(Category=Category, add_money="Expense")
            for item in filtered_by_category:
                quantity += item.quantity
            return quantity

        for y in Category_list:
            finalrep[y] = get_expense_category_amount(y)

        return JsonResponse({'expense_category_data': finalrep}, safe=False)

class Info(View):
    def get(self, request):
        return render(request, 'home/info.html')
     