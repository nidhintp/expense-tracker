from django.shortcuts import render,redirect
from django import forms
from django.views.generic import View
from budget.models import Transactions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import never_cache

def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,never_cache]
class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transactions
        exclude=("created_date","user_object",)
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})


        }
        # fields="__all__"
        # fields=["title","amount","type","category","user"]

    # title=forms.CharField()
    # amount=forms.IntegerField()
    # type=forms.CharField()
    # category=forms.CharField()
    # user=forms.CharField()
        


class RegistrationForm(forms.ModelForm):
    class  Meta:
        model=User
        fields=["username","password","email"]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"}),
        }


class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))


# view for listing all transaction
# url implemenet:local host:8000/transactions/all/
@method_decorator(decs,name="dispatch")
class TransactionList(View):
    def get(self,request,*args,**kwargs):
        qs=Transactions.objects.filter(user_object=request.user)
        current_month=timezone.now().month
        current_year=timezone.now().year
        print(current_month,current_year)
        data=Transactions.objects.filter(
            created_date__month=current_month,
            created_date__year=current_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)

        cat_qs=Transactions.objects.filter(
            created_date__month=current_month,
            created_date__year=current_year,
            user_object=request.user
        ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_qs)





        # expense_total=Transactions.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=current_month,
        #     created_date__year=current_year,
        # ).aggregate(Sum("amount"))
        # print(expense_total)
        # income_total=Transactions.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=current_month,
        #     created_date__year=current_year,
        # ).aggregate(Sum("amount"))
        # print(income_total)
        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat_data":cat_qs})

# views for creating new transaction
    # url:localhost/8000/transaction/add/
    # method:get,post
@method_decorator(decs,name="dispatch")

class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_add.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)
        if form.is_valid():
            # data=form.cleaned_data
            # Transactions.objects.create(**data)

            # form.save()
            data=form.cleaned_data
            Transactions.objects.create(**data,user_object=request.user)
            messages.success(request,"transaction has been added successfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"failed to add transaction")
            return render(request,"transaction_add.html",{"form":form})

# url:localhost:8000/transaction/{id}/
        # method:get
@method_decorator(decs,name="dispatch")
class TransactionDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Transactions.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})
    
# transaction Delete
# url-localhost:8000/transactions/{id}/remove/
    # method get
@method_decorator(decs,name="dispatch")
class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transactions.objects.filter(id=id).delete()
        messages.success(request,"transaction has been removed successully")
        return redirect("transaction-list")
    

# transaction edit
    # url-localhost:8000/transactions/{id}/update/
    # method:get,post
method_decorator(decs,name="dispatch")
class TransactionUpdate(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transactions.objects.get(id=id)
        form=TransactionForm(instance=transaction_object)
        return render(request,"transaction_edit.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transactions.objects.get(id=id)
        form=TransactionForm(request.POST,instance=transaction_object)
        if form.is_valid():
            form.save()
            messages.success(request,"transaction has been updated successfully")
            return redirect("transaction-list")
        else:
          messages.error(request,"failed to update transaction")
          return render(request,"transaction_edit.html",{"form":form})



# signup
# url:localhost:8000/signup/
# method=get,post
        
class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            # form.save()can't encrypt password
            User.objects.create_user(**form.cleaned_data)
            print("created")
            return redirect("signin")
        else:
            print("faild")
            return render(request,"register.html",{"form":form})
        

        
# signin
 # localhost:800/signin/
        

class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"signin.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            usr_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=usr_name,password=pwd)
            if user_object:
                print("valid credentials")
                login(request,user_object)
                return redirect("transaction-list")
        print("invalid credentials")
        return render(request,"signin.html",{"form":form})

@method_decorator(decs,name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")