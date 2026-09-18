from pyexpat.errors import messages

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from .models import  Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

# Query -> Malumotlarni bazadan olish qismi QUERY deyiladi
class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)

    def resolve_all_products(self, info):
        return Product.objects.all()


# Mutation ->  Malumotlarni o'zgartirish saqlash o'chirish MUTATION deyiladi
class CreateProduct(graphene.Mutation):
    message = graphene.String()
    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Int(required=True)
        stock = graphene.Int(required=True)

    def mutate(self, info, title, price, stock):
        Product.objects.create(title=title , price=price, stock=stock)
        return CreateProduct(message = "yaratildi")

# #
class UpdateProduct(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        stock = graphene.Int()
        price = graphene.Int()

    def mutate(self, info, id, title=None, stock=None, price=None):
        product = Product.objects.get(pk=id)
        if title:
            product.title = title
        if stock:
            product.stock = stock
        if price:
            product.price = price


        product.save()
        return UpdateProduct(message="Post o'zgartirildi")

class DeleteProduct(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)


    def mutate(self, info, id):
        query = Product.objects.filter(pk=id)
        if query.exists():
            query.delete()
        return UpdateProduct(message="Post o'chirildi")


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

# # Asosiy schema
schema = graphene.Schema(query=Query, mutation=Mutation)