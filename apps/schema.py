import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Product


def require_staff(info):
    """Mutatsiyalar faqat staff foydalanuvchiga (/admin/ orqali kirgan sessiya)."""
    user = info.context.user
    if not (user.is_authenticated and user.is_staff):
        raise GraphQLError("Ruxsat yo'q: bu amal uchun admin sifatida kiring.")


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
        require_staff(info)
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
        require_staff(info)
        product = Product.objects.filter(pk=id).first()
        if product is None:
            raise GraphQLError("Mahsulot topilmadi")
        # `is not None`: 0 ham to'g'ri qiymat (narx/qoldiq 0 ga tushirilishi mumkin)
        if title is not None:
            product.title = title
        if stock is not None:
            product.stock = stock
        if price is not None:
            product.price = price


        product.save()
        return UpdateProduct(message="Post o'zgartirildi")

class DeleteProduct(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)


    def mutate(self, info, id):
        require_staff(info)
        query = Product.objects.filter(pk=id)
        if query.exists():
            query.delete()
        return DeleteProduct(message="Post o'chirildi")


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

# # Asosiy schema
schema = graphene.Schema(query=Query, mutation=Mutation)