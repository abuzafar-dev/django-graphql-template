import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

from apps.models import Product


class MutationPermissionTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(title="Phone", price=100, stock=5)

    def gql(self, client, query):
        response = client.post("/graphql/", json.dumps({"query": query}), content_type="application/json")
        return response.json()

    def test_query_is_public(self):
        data = self.gql(Client(), "{ allProducts { id title } }")
        self.assertEqual(data["data"]["allProducts"][0]["title"], "Phone")

    def test_anonymous_cannot_mutate(self):
        client = Client()
        for mutation in (
            'mutation { createProduct(title: "X", price: 1, stock: 1) { message } }',
            'mutation { updateProduct(id: %d, title: "Hacked") { message } }' % self.product.id,
            'mutation { deleteProduct(id: %d) { message } }' % self.product.id,
        ):
            data = self.gql(client, mutation)
            self.assertIn("errors", data, mutation)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Phone")
        self.assertEqual(Product.objects.count(), 1)

    def test_regular_user_cannot_mutate(self):
        client = Client()
        client.force_login(User.objects.create_user("ali", password="x"))
        data = self.gql(client, 'mutation { deleteProduct(id: %d) { message } }' % self.product.id)
        self.assertIn("errors", data)
        self.assertTrue(Product.objects.exists())

    def test_staff_can_mutate(self):
        client = Client()
        client.force_login(User.objects.create_user("admin", password="x", is_staff=True))
        data = self.gql(client, 'mutation { deleteProduct(id: %d) { message } }' % self.product.id)
        self.assertNotIn("errors", data)
        self.assertFalse(Product.objects.exists())


class UpdateValuesTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(title="Phone", price=100, stock=5)
        self.client = Client()
        self.client.force_login(User.objects.create_user("admin", password="x", is_staff=True))

    def gql(self, query):
        return self.client.post("/graphql/", json.dumps({"query": query}), content_type="application/json").json()

    def test_explicit_zero_is_saved(self):
        data = self.gql('mutation { updateProduct(id: %d, price: 0, stock: 0) { message } }' % self.product.id)
        self.assertNotIn("errors", data)
        self.product.refresh_from_db()
        self.assertEqual((self.product.price, self.product.stock), (0, 0))

    def test_omitted_fields_unchanged(self):
        self.gql('mutation { updateProduct(id: %d, title: "Yangi") { message } }' % self.product.id)
        self.product.refresh_from_db()
        self.assertEqual((self.product.title, self.product.price, self.product.stock), ("Yangi", 100, 5))

    def test_unknown_product_gives_clean_error(self):
        data = self.gql('mutation { updateProduct(id: 999, title: "X") { message } }')
        self.assertEqual(data["errors"][0]["message"], "Mahsulot topilmadi")

    def test_delete_returns_message(self):
        data = self.gql('mutation { deleteProduct(id: %d) { message } }' % self.product.id)
        self.assertEqual(data["data"]["deleteProduct"]["message"], "Post o'chirildi")
