from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from decimal import Decimal
from .models import Product, Producer, Manufacturer, CategoryProduct

# 1. Product.get_final_price()
class ProductFinalPriceTest(TestCase):
    """
    Тестирование метода Product.get_final_price().
    Проверяется корректность расчёта цены при разных значениях скидки.
    """
    def setUp(self):
        self.producer = Producer.objects.create(name="Kari")
        self.manufacturer = Manufacturer.objects.create(name="Kari")
        self.category = CategoryProduct.objects.create(name="Кроссовки")
    def _make_product(self, price, discount):
        return Product.objects.create(
            article="А145Т4",
            product="Кроссовки Kari",
            price=Decimal(str(price)),
            discount=Decimal(str(discount)),
            amount_on_warehouse=Decimal("10"),
            description="Тестовый товар",
            producer=self.producer,
            manufacturer=self.manufacturer,
            category=self.category,
        )
    def test_final_price_with_discount(self):
        product = self._make_product(price=1000, discount=20)
        self.assertEqual(
            product.get_final_price(),
            Decimal("800.00"),
            msg="Цена со скидкой 20% должна быть 800.00"
        )
    def test_final_price_without_discount(self):
        product = self._make_product(price=1500, discount=0)
        self.assertEqual(
            product.get_final_price(),
            Decimal("1500.00"),
            msg="При нулевой скидке цена должна быть равна исходной"
        )

# 2. login_view
class LoginViewTest(TestCase):
    """
    Тестирование login_view:
    - успешная авторизация
    - неверные данные
    - GET-запрос
    - logout
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPass123",
            first_name="Иван"
        )
        self.login_url = reverse("login")
        self.home_url = reverse("home")
    def test_successful_login_redirects_and_authenticates(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "StrongPass123",
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertIn('_auth_user_id', self.client.session)
    def test_invalid_credentials_return_error(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "WrongPassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    def test_empty_credentials(self):
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
    def test_get_login_page_returns_200(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
    def test_logout(self):
        self.client.login(username="testuser", password="StrongPass123")
        self.client.logout()
        response = self.client.get(self.home_url)
        self.assertRedirects(
            response,
            f"{self.login_url}?next={self.home_url}"
        )
# 3. home_view — проверка роли
class HomeViewRoleTest(TestCase):
    """
    Проверка определения роли пользователя в home_view.
    """
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home")
        self.login_url = reverse("login")
    def _login_and_get(self, user):
        self.client.force_login(user)
        return self.client.get(self.home_url)
    def test_superuser_role_is_administrator(self):
        admin = User.objects.create_superuser(
            username="admin",
            password="Admin@123"
        )
        response = self._login_and_get(admin)
        self.assertEqual(response.status_code, 200)
        self.assertIn("role", response.context)
        self.assertEqual(response.context["role"], "Администратор")
    def test_manager_group_role(self):
        manager_group, _ = Group.objects.get_or_create(name="Менеджер")
        manager = User.objects.create_user(
            username="manager",
            password="Manager@123"
        )
        manager.groups.add(manager_group)
        response = self._login_and_get(manager)
        self.assertEqual(response.status_code, 200)
        self.assertIn("role", response.context)
        self.assertEqual(response.context["role"], "Менеджер")
    def test_regular_user_role(self):
        user = User.objects.create_user(
            username="client",
            password="Client@123"
        )
        response = self._login_and_get(user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("role", response.context)
        self.assertEqual(response.context["role"], "Авторизованный пользователь")
    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(
            response,
            f"{self.login_url}?next={self.home_url}"
        )