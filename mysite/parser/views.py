from django.shortcuts import render, redirect
from collections import namedtuple
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from tabulate import tabulate
import re
import datetime

from .models import *
from django.views.generic.base import TemplateView
from .forms import *
from django.views.generic.edit import FormView

from django.http import HttpResponseRedirect
import json
from django.contrib import messages
from django.views.generic.base import RedirectView

from django.urls import reverse_lazy
from .urls import *

class HomeView(TemplateView):
	template_name ='parser/home.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

class ParseInputView(FormView):
    template_name = "parser/input2.html"
    form_class=DateInputForm
    success_url = reverse_lazy('parser:parsing')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countryCurrency"] = 0
        #context["form3"] = DateInputForm
        #print(context)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            date1 = request.POST.get("date1","")
            date2 = request.POST.get("date2","")
            self.request.session['date1'] = date1
            self.request.session['date2'] = date2

            d1 = date1.split("-")
            #print("date1", date1)
            y1 = int(d1[0])

            d2 = date2.split("-")
            y2 = int(d2[0])

            d1 = date1.split("-")
            y1 = int(d1[0])
            m1 = int(d1[1])
            d1 = int(d1[2])

            d2 = date2.split("-")
            y2 = int(d2[0])
            m2 = int(d2[1])
            d2 = int(d2[2])

            diff = str(datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1))
            diff = diff.split(" ")

            if not(726<=int(diff[0])<=733):
            	print("НЕВЕРНЫЙ ДИАПАЗОН ДАТ")
            	messages.info(request, 'Неверный диапазон дат')
            	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            try:
	            self.request.session['date1'] = date1
	            self.request.session['date2'] = date2
	            print(request.POST)
	            messages.info(request, 'Начинаем парсинг')
	            return redirect("parser:parsing")
            except:
            	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            



class ParsingView(RedirectView):
    url = reverse_lazy("parser:home")

    def get_redirect_url(self,*args, **kwargs):
    	messages.info(self.request, 'Данные успешно обновлены')
    	#print('PARSING')
    	date1 = self.request.session.get('date1',0)
    	date2 = self.request.session.get('date2',0)
    	#print(date1, " ",date2)
    	date1 = str(date1).split("-")
    	by = int(date1[0])
    	bm = int(date1[1])
    	bd= int(date1[2])
    	date2 = str(date2).split("-")
    	ey = int(date2[0])
    	em = int(date2[1])
    	ed= int(date2[2])

    	currency_list = {"52148":"Доллар США","52170":"Евро","52146":"Фунт Стерлингов","52246":"Йена","52158":"Турецкая лира","52238":"Индийская рупия","52207":"Китайский юань"}

    	#get country + currency
    	url = f'https://www.iban.ru/currency-codes'
    	try:
    		response = requests.get(f"{url}")
    	except:
    		print("Error while tracking")
    	if response:
    		soup = bs(response.content,'lxml')
    		table = soup.find('table', attrs={'class':'table table-bordered downloads tablesorter'})
    		df = pd.read_html(str(table),parse_dates=True, thousands='.',decimal=',')
    		df = df[0].drop('Код', axis=1)
    		df2 = df.drop('Номер', axis=1)
    		res2 = tabulate(df2, headers='keys', tablefmt='psql')
    		#print(res2)

    	for cur,val in currency_list.items():
    		temp2 = df2.loc[df2['Валюта'] == val]
    		country_list = temp2['Страна']
    		#print("countries = ", countries)

    		url = f'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={cur}&bd={bd}&bm={bm}&by={by}&ed={ed}&em={em}&ey={ey}&x=48&y=13#archive'
    		try:
    			response = requests.get(f"{url}")
    		except:
    			print("ERROR IN RESPONSE")
    		if response:
    			soup = bs(response.content,'lxml')
    			table = soup.find('table', attrs={'class':'karramba'})
    			df = pd.read_html(str(table),parse_dates=True, thousands='.',decimal=',')
    			df = df[0].drop('Кол-во', axis=1)
    			df1 = df.drop('Дата', axis=1)
    			res1 = tabulate(df1, headers='keys', tablefmt='psql')
    			if not self.request.POST.get("mydates",""):
    				df = pd.read_html(str(table),parse_dates=True)
    				df = df[0].drop('Кол-во', axis=1)
    				df = df.drop('Курс', axis=1)
    				mydates = df.drop('Изменение', axis=1)
    				self.request.session['mydates'] = mydates.to_json()

    			for i in range(mydates.shape[0]):
		        	date1 = mydates.take([i])['Дата'].to_string(index=False)
		        	date1 = date1.split(".")
	        		y = int(date1[2])
	        		m = int(date1[1])
	        		d= int(date1[0])
	        		date1 = datetime.date(y, m, d)
	        		exists1=Date.objects.filter(date=date1)
	        		if not exists1:
	        			date_obj = Date.objects.create(date=date1)

	        			try:
	        				value1 = df1.take([i])['Курс'].to_string(index=False)
	        				value2 = df1.take([i])['Изменение'].to_string(index=False)
	        				for country in country_list:
	        					country = str(country)
	        					country_obj = CountryCurrency.objects.create(date=date_obj,currency=val,country=country,value=value1)
	        					CurrencyChange.objects.create(country=country_obj,change=value2)
	        			except Exception as e:
	        				pass
	        		else:
	        			date_obj = Date.objects.get(date=date1)
	        			try:
		        			value1 = df1.take([i])['Курс'].to_string(index=False)
		        			value2 = df1.take([i])['Изменение'].to_string(index=False)
		        			for country in country_list:
			        			exists2=CountryCurrency.objects.filter(date=date_obj,currency=val,country=country)
			        			if not exists2:
			        				country = str(country)
			        				country_obj = CountryCurrency.objects.create(date=date_obj,currency=val,country=country,value=value1)
		        					CurrencyChange.objects.create(country=country_obj,change=value2)
	        			except Exception as e:
	        				pass
    	
    	return super().get_redirect_url(*args,**kwargs)


class ChartView(TemplateView):
	template_name ='parser/index.html'

	def get_context_data(self, **kwargs):
		labels = []
		data1 = []
		data2 = []
		data3 = []
		data4 = []
		data5 = []
		
		date1 = self.request.session.get('date1',"")
		date2 = self.request.session.get('date2',"")
		mydates = pd.date_range(date1, date2)


		#mydates=json.loads(mydates)
		#mydates=pd.DataFrame(mydates)

		data={}
		label_names={}

		data['data1'] = []
		data["data2"] = []
		data["data3"] = []
		data["data4"] = []
		data["data5"] = []

		

		for i in range(mydates.shape[0]):
			date1 = str(mydates.take([i])[0])
			
			date1 = date1.split(" ")[0]
			
			date1 = date1.split("-")
			y = int(date1[0])
			m = int(date1[1])
			d= int(date1[2])
			date1 = str(datetime.date(y, m, d))
			print("!date1 = ",date1)
			try:
				date_obj=Date.objects.get(date=date1)
			except:
				continue
			rel_date=date_obj.date
			labels.append(str(rel_date))

			for i in range(1,6):
				label_name=f'label{i}'
				label_names[label_name] = f""" "# {self.request.session.get(f'country{i}',0)}" """
				try:
					country_name = self.request.session.get(f'country{i}',0)
					#print("country_name = ",country_name)
					country_obj = CountryCurrency.objects.get(date=date_obj,country=country_name)
					
					change_obj = CurrencyChange.objects.get(country=country_obj)
					change = change_obj.change
					print("country_name = ",change)
					data_name=f'data{i}'
					data[data_name].append(float(str(change)))
				except Exception as e:
					print(e)
					change=0
				finally:
					data_name=f'data{i}'
					data[data_name].append(float(str(change)))


		if any(data['data1']):
			data1=data['data1']
		else:
			data1 = []

		if any(data['data2']):
			data2=data['data2']
		else:
			data2 = []

		if any(data['data3']):
			data3=data['data3']
		else:
			data3 = []

		if any(data['data4']):
			data4=data['data4']
		else:
			data4 = []

		if any(data['data5']):
			data5=data['data5']
		else:
			data5 = []

		label1=label_names['label1']
		label2=label_names['label2']
		label3=label_names['label3']
		label4=label_names['label4']
		label5=label_names['label5']
		"""
		for key, value in self.request.session.items():
			print('{} => {}'.format(key, value))
		"""

		context={'labels':labels,'data1':data1,'data2':data2,'data3':data3,'data4':data4,'data5':data5,'label1':label1,'label2':label2,'label3':label3,'label4':label4,'label5':label5}
		return context




            




class ChartInputView(FormView):
    template_name = "parser/input.html"
    form_class=DateInputForm
    #success_url = '/res'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            
            country1 = request.POST.get("country1","")
            country2 = request.POST.get("country2","")
            country3 = request.POST.get("country3","")
            country4 = request.POST.get("country4","")
            country5 = request.POST.get("country5","")
            date1 = request.POST.get("date1","")
            date2 = request.POST.get("date2","")

            try:
            	#self.request.session['country'] = country
	            self.request.session['country1'] = country1
	            self.request.session['country2'] = country2
	            self.request.session['country3'] = country3
	            self.request.session['country4'] = country4
	            self.request.session['country5'] = country5
	            self.request.session['date1'] = date1
	            self.request.session['date2'] = date2
	            print(request.POST)
	            return redirect("parser:chart_display")
            except:
            	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form2"] = CountyInputForm
        return context

    def form_valid(self, form):
        return super().form_valid(form)



