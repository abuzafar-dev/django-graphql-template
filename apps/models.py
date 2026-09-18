from django.db.models.base import Model
from django.db.models.fields import IntegerField, CharField, DecimalField


class Product(Model):
    title = CharField(max_length=100)
    price = DecimalField(max_digits=12, decimal_places=0)
    stock = IntegerField(null=True)


