from django.db import models



class Date(models.Model):
	date = models.DateField('Дата',blank=False)

	def __str__(self):
		return str(self.date)

	class Meta:
		ordering = ('-date',)

class CountryCurrency(models.Model):
	country = models.CharField('Страна',max_length=200, blank=False)
	currency = models.CharField('Валюта',max_length=200, blank=False)
	date = models.ForeignKey(Date, on_delete=models.CASCADE, blank=True)
	value = models.FloatField(default=0, blank=True)

	def save(self, *args, **kwargs):
		print("SAVING MODEL......")
		return super().save(*args, **kwargs)

	def update(self, *args, **kwargs):
		print("UPDATING MODEL....")
		super().update(**kwargs)

	def __str__(self):
		return str(self.country)

	def create(self, **obj_data):
		print("CREATING MODEL......")
		return super().create(**obj_data)

class CurrencyChange(models.Model):
	country = models.ForeignKey(CountryCurrency, on_delete=models.CASCADE, blank=True)
	change = models.FloatField('Относительное изменение',default=0, blank=True)

	def __str__(self):
		return str(self.change)

