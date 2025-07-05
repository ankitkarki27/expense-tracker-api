# main/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from main.models import ExpenseIncome

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """
    Utility helpers for creating users and JWT headers.
    """

    def create_user(self, username, email, password, is_superuser=False):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=is_superuser,
            is_staff=is_superuser,
        )

    def auth_headers(self, user):
        access = RefreshToken.for_user(user).access_token
        return {"HTTP_AUTHORIZATION": f"Bearer {access}"}


class ExpenseTrackerTests(BaseAPITestCase):
    """
    End-to-end tests covering auth, CRUD, permissions, pagination,
    business logic, and status codes.
    """

    def setUp(self):
        self.user = self.create_user("testuser", "user@test.com", "Testpass123!")
        self.superuser = self.create_user("admin", "admin@test.com", "Adminpass123!", True)

        self.expense1 = ExpenseIncome.objects.create(
            user=self.user,
            title="User Expense Flat",
            description="desc1",
            amount=100,
            transaction_type="debit",
            tax=10,
            tax_type="flat",
        )
        self.expense2 = ExpenseIncome.objects.create(
            user=self.user,
            title="User Expense Percentage",
            description="desc2",
            amount=100,
            transaction_type="debit",
            tax=10,
            tax_type="percentage",
        )
        self.expense3 = ExpenseIncome.objects.create(
            user=self.superuser,
            title="Admin Expense",
            description="desc3",
            amount=200,
            transaction_type="credit",
            tax=20,
            tax_type="flat",
        )

        self.client = APIClient()

    # ---------- helpers -------------------------------------------------
    def authenticate(self, username, password):
        url = reverse("login")
        res = self.client.post(url, {"username": username, "password": password}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    # ---------- auth tests ----------------------------------------------
    def test_user_registration(self):
        url = reverse("register")
        payload = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "Newpass123!",
            "password2": "Newpass123!",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_and_token(self):
        url = reverse("login")
        res = self.client.post(url, {"username": "testuser", "password": "Testpass123!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    # ---------- CRUD & business-logic tests -----------------------------
    def test_create_expense_flat_tax(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-list")
        payload = {
            "title": "Lunch",
            "description": "Burger",
            "amount": 100,
            "transaction_type": "debit",
            "tax": 10,
            "tax_type": "flat",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(res.data["total_amount"]), 110.0)

    def test_create_expense_percentage_tax(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-list")
        payload = {
            "title": "Bonus",
            "description": "Performance",
            "amount": 200,
            "transaction_type": "credit",
            "tax": 10,
            "tax_type": "percentage",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(res.data["total_amount"]), 220.0)

    def test_list_expenses_pagination(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-list") + "?page=1&page_size=2"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(res.data["results"]), 2)

    def test_list_expenses_owner_only(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [e["title"] for e in res.data["results"]]
        self.assertIn("User Expense Flat", titles)
        self.assertNotIn("Admin Expense", titles)

    def test_superuser_sees_all_records(self):
        self.authenticate("admin", "Adminpass123!")
        url = reverse("expense-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [e["title"] for e in res.data["results"]]
        self.assertIn("Admin Expense", titles)
        self.assertIn("User Expense Flat", titles)

    def test_retrieve_expense_permission(self):
        self.authenticate("testuser", "Testpass123!")
        # Own record → OK
        url_own = reverse("expense-detail", args=[self.expense1.id])
        res = self.client.get(url_own)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Other user's record → should be 404 (not in queryset)
        url_other = reverse("expense-detail", args=[self.expense3.id])
        res = self.client.get(url_other)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_expense(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-detail", args=[self.expense1.id])
        payload = {
            "title": "Updated Expense",
            "description": "Updated desc",
            "amount": 120,
            "transaction_type": "debit",
            "tax": 12,
            "tax_type": "flat",
        }
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Updated Expense")
        self.assertEqual(float(res.data["total_amount"]), 132.0)

    def test_delete_expense(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-detail", args=[self.expense2.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ExpenseIncome.objects.filter(id=self.expense2.id).exists())

    def test_unauthenticated_access(self):
        url = reverse("expense-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_amount_or_tax(self):
        self.authenticate("testuser", "Testpass123!")
        url = reverse("expense-list")

        # Negative amount
        bad_amount = {
            "title": "Bad",
            "description": "",
            "amount": -10,
            "transaction_type": "debit",
            "tax": 5,
            "tax_type": "flat",
        }
        res1 = self.client.post(url, bad_amount, format="json")
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        # Negative tax
        bad_tax = bad_amount.copy()
        bad_tax["amount"] = 100
        bad_tax["tax"] = -5
        res2 = self.client.post(url, bad_tax, format="json")
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
