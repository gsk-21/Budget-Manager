import base64

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from .models import Income, Expense, Profile
import json
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.db import models


def get_number(amount, key):
    return float(decrypt(amount, key))


def formated(num):
    return format(num, '.2f')


# date.strftime('%B')
def home(request):
    date = timezone.now()
    context = initialize()
    if request.user.is_authenticated:
        user = request.user
        # incomes = Income.objects.filter(user=user)
        # expenses = Expense.objects.filter(user=user)
        incomes = Income.objects.filter(user=user).filter(datetime__month=date.month).filter(datetime__year=date.year)
        expenses = Expense.objects.filter(user=user).filter(datetime__month=date.month).filter(datetime__year=date.year)

        key = Profile.objects.get(user=user).key
        incomes, expenses = decrypt_list(key, incomes, expenses)

        context['incomes'] = incomes
        context['expenses'] = expenses

        total_income, total_expense = get_totalIncExp(incomes, expenses, key)
        savings = total_income - total_expense
        if savings < 1:
            savings = 0

        overall_budget = get_overall_budget(user, key)
        context['total_income'] = format(total_income, '.2f')
        context['total_expense'] = format(total_expense, '.2f')
        context['savings'] = format(savings, '.2f')
        context['overall_income'] = overall_budget['overall_income']
        context['overall_expense'] = overall_budget['overall_expense']
        context['overall_savings'] = overall_budget['overall_savings']
        context['overall_inc_percentage'] = overall_budget['overall_inc_percentage']
        context['overall_exp_percentage'] = overall_budget['overall_exp_percentage']
        context['overall_savings_percentage'] = overall_budget['overall_savings_percentage']

    return render(request, 'home.html', context)


def initialize():
    context = {}
    date = timezone.now()
    month = date.strftime('%B')
    context['month'] = month
    context['year'] = date.year
    context['total_income'] = 0.00
    context['total_expense'] = 0.00
    context['savings'] = 0.00
    context['overall_income'] = 0.00
    context['overall_expense'] = 0.00
    context['overall_savings'] = 0.00
    context['overall_inc_percentage'] = 0.00
    context['overall_exp_percentage'] = 0.00
    context['overall_savings_percentage'] = 0.00
    return context


def monthly_budget(request):
    context = {}
    # date = timezone.now()

    if request.user.is_authenticated:
        user = request.user
        key = Profile.objects.get(user=user).key
        incomes = Income.objects.filter(user=user)
        expenses = Expense.objects.filter(user=user)
        years = set()
        for i in incomes:
            years.add(i.datetime.year)
        for i in expenses:
            years.add(i.datetime.year)
        years = list(years)
        years.sort()
        years.reverse()
        year_dict = {}
        import os
        os.system('cls')

        for year in years:
            yearly_total = {}
            budget_list = []
            temp_list = []
            yearly_income, yearly_inc_percent = 0, 0
            yearly_expense, yearly_exp_percent = 0, 0
            yearly_savings, yearly_savings_percent = 0, 0
            for i in range(1, 13):
                temp_date = date(year=year, month=i, day=1)
                month = temp_date.strftime('%B')
                month_number = i
                income_list = incomes.filter(datetime__year=year).filter(datetime__month=i)
                expense_list = expenses.filter(datetime__year=year).filter(datetime__month=i)
                total_income, total_expense = 0, 0
                for i in income_list:
                    try:
                        total_income = total_income + get_number(i.amount, key)
                    except:
                        total_income = total_income + i.amount
                for i in expense_list:
                    try:
                        total_expense = total_expense + get_number(i.amount, key)
                    except:
                        total_expense = total_expense + i.amount
                # total_income = formated(total_income)
                # total_expense = formated(total_expense)
                # total_income = income_list.aggregate(Sum('amount'))['amount__sum']
                # total_expense = expense_list.aggregate(Sum('amount'))['amount__sum']
                savings = total_income - total_expense

                expense_percent = 0
                savings_percent = 0
                income_percent = 0
                # print("\nTotal Income:", total_income, "\nTotal Expense:", total_expense)
                if savings != 0:
                    if total_income > 0 and total_expense > 0:
                        income_percent = 100
                        if int(total_income) > 0:
                            expense_percent = int(round(((int(total_expense) / int(total_income)) * 100), 0))
                        else:
                            expense_percent = 0
                        savings_percent = 100 - expense_percent
                        if expense_percent == 0:
                            savings_percent = 0
                    if total_expense == 0:
                        income_percent = 100
                        savings_percent = 100
                        total_expense = 0
                    if total_income == 0:
                        total_income = 0
                        savings = 0
                    yearly_income = yearly_income + total_income
                    yearly_expense = yearly_expense + total_expense
                    yearly_savings = yearly_savings + savings

                    budget_dict = {'month': month, 'income': str(total_income), 'month_number': month_number,
                                   'expense': str(total_expense),
                                   'savings': str(savings),
                                   'savings_percent': formated(savings_percent),
                                   'expense_percent': expense_percent,
                                   'income_percent': income_percent
                                   }
                    budget_list.append(budget_dict)
            budget_list.reverse()
            # print(year, "  -  ", yearly_income, "  ", yearly_expense, "  ", yearly_savings)
            if (yearly_expense < yearly_income):
                yearly_inc_percent = 100
                yearly_exp_percent = int(round(((int(yearly_expense) / int(yearly_income)) * 100),0))
                yearly_savings_percent = (100 - yearly_exp_percent)
            yearly_total[year] = {'yearly_income': yearly_income,
                                  'yearly_expense': yearly_expense,
                                  'yearly_savings': yearly_savings,
                                  'yearly_inc_percent': yearly_inc_percent,
                                  'yearly_exp_percent': yearly_exp_percent,
                                  'yearly_savings_percent': yearly_savings_percent
                                  }
            temp_list = [budget_list, [yearly_total]]
            year_dict[year] = temp_list

        # context['incomes'] = incomes
        # context['expenses'] = expenses
        context['budgets'] = year_dict

        return render(request, 'monthly_budget.html', context)
    else:
        return redirect('login')


def single_month_budget(request, month, year):
    context = {'month_num': month}
    if request.user.is_authenticated:
        user = request.user
        key = Profile.objects.get(user=user).key

        incomes = Income.objects.filter(user=user).filter(datetime__month=month).filter(datetime__year=year)
        expenses = Expense.objects.filter(user=user).filter(datetime__month=month).filter(datetime__year=year)
        incomes, expenses = decrypt_list(key, incomes, expenses)
        context['incomes'] = incomes
        context['expenses'] = expenses
        total_income, total_expense = get_totalIncExp(incomes, expenses, key)
        savings = total_income - total_expense
        if savings < 1:
            savings = 0
        temp_date = date(year=year, month=month, day=1)
        month = temp_date.strftime('%B')
        context['year'] = year
        context['month'] = month
        context['total_income'] = formated(total_income)
        context['total_expense'] = formated(total_expense)
        context['savings'] = formated(savings)

    return render(request, "single_month_budget.html", context)


def add_item(request):
    result = ''
    if request.user.is_authenticated:
        budget_type = request.POST.get('type')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        date = parse_date(date_str)
        user = request.user
        key = Profile.objects.get(user=user).key
        if budget_type == 'inc':
            income = Income()
            income.user = user
            income.amount = encrypt(str(amount).encode(), key)
            income.description = encrypt(description.encode(), key)
            income.datetime = date
            income.save()
            result = 'Income added'

        elif budget_type == 'exp':
            expense = Expense()
            expense.user = user
            expense.amount = encrypt(str(amount).encode(), key)
            expense.description = encrypt(description.encode(), key)
            expense.datetime = date
            expense.save()
            result = 'Expense added'

        return HttpResponse(
            json.dumps({'result': result}),
            content_type="application/json"
        )
    else:
        result = "Login required"
        return HttpResponse(
            json.dumps({'result': result}),
            content_type="application/json"
        )


def remove_item(request):
    user = request.user
    if user.is_authenticated:
        budget_type = request.POST.get('type')
        slug = request.POST.get('slug')
        result = ''
        if budget_type == 'inc':
            income = Income.objects.get(slug=slug)
            if income.user == request.user:
                income.delete()
                result = 'Income removed'
            else:
                return HttpResponse("Access Denied")
        elif budget_type == 'exp':
            expense = Expense.objects.get(slug=slug)
            if expense.user == request.user:
                expense.delete()
                result = 'Expense removed'
            else:
                return HttpResponse("Access Denied")
        return HttpResponse(json.dumps({'result': result}), content_type="application/json")
    else:
        return HttpResponse("Login Required")


# Helper function
def get_overall_budget(user, key):
    context = {}
    total_income = 0
    total_expense = 0
    total_inc_percentage = 0
    total_exp_percentage = 0
    total_savings_percentage = 0
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)
    for i in incomes:
        try:
            total_income = total_income + get_number(i.amount, key)
        except Exception as e:
            total_income = total_income + float(i.amount)

    for i in expenses:
        try:
            total_expense = total_expense + get_number(i.amount, key)
        except Exception as e:
            total_expense = total_expense + float(i.amount)

    savings = total_income - total_expense
    if savings < 1:
        savings = 0
    if total_expense < total_income:
        total_inc_percentage = 100
        total_exp_percentage = round(((int(total_expense) / int(total_income)) * 100), 2)
        total_savings_percentage = total_inc_percentage - total_exp_percentage
    context['overall_income'] = formated(total_income)
    context['overall_expense'] = formated(total_expense)
    context['overall_savings'] = formated(savings)
    context['overall_inc_percentage'] = total_inc_percentage
    context['overall_exp_percentage'] = total_exp_percentage
    context['overall_savings_percentage'] = total_savings_percentage
    return context


def get_totalIncExp(incomes, expenses, key):
    total_income, total_expense = 0, 0
    for i in incomes:
        try:
            total_income = total_income + get_number(i.amount, key)
        except Exception as e:
            total_income = total_income + float(i.amount)

    for i in expenses:
        try:
            total_expense = total_expense + get_number(i.amount, key)
        except Exception as e:
            total_expense = total_expense + float(i.amount)
    return total_income, total_expense


def decrypt_list(key, incomes, expenses):
    for i in incomes:
        try:
            i.description = decrypt(i.description, key)
            i.amount = formated(get_number(i.amount, key))
        except:
            i.description = i.description
            i.amount = formated(float(i.amount))

    for i in expenses:
        try:
            i.description = decrypt(i.description, key)
            i.amount = formated(get_number(i.amount, key))
        except:
            i.description = i.description
            i.amount = formated(float(i.amount))
    return incomes, expenses


def sign_up(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        confirm_password = request.POST.get('confirm-password')
        context = {'username': username, 'name': name}
        t = name.replace(" ", '')

        if not t.isalpha():
            context['error'] = 'Name Should contain only alphabets'
            return render(request, 'sign-up.html', context)

        if validate_username_unique(username):
            context['error'] = 'Username taken'
            return render(request, 'sign-up.html', context)

        if len(password) < 8:
            context['error'] = 'Make sure your password contains at least 8 characters'
            return render(request, 'sign-up.html', context)

        if password != confirm_password:
            context['error'] = 'Password mismatch'
            return render(request, 'sign-up.html', context)

        user = User.objects.create_user(username=username, password=password, first_name=name)
        profile = Profile()
        profile.user = user
        profile.save()
        return redirect('login')
    else:
        return render(request, 'sign-up.html', {})


def set_theme(request):
    if request.user.is_authenticated:
        print("In set theme...")
        user = request.user
        theme = request.POST.get('theme')
        user = request.user
        profile = Profile.objects.get(user=user)
        profile.theme = theme
        profile.save()
        print(theme)
        return HttpResponse(theme)
    else:
        return HttpResponse("Login to set theme")

# Helper function
def validate_username_unique(value):
    exists = User.objects.filter(username=value)
    if exists:
        return 1

def encrypt(data: bytes, key: bytes):
    return Fernet(key).encrypt(data)


def decrypt(token: bytes, key: bytes):
    return Fernet(key).decrypt(token).decode("utf-8")


