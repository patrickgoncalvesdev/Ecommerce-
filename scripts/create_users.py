from decimal import Decimal
from ecommerce.models import AdministrativeUser, Affiliate
from django.contrib.auth.hashers import make_password

from ecommerce.models.administration import AdministrativeProfile
from ecommerce.models.modality import Modality
from ecommerce.models.quotation import Quotation
from ecommerce.models.affiliate_quotation import AffiliateQuotation
from django.db import transaction
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group, Permission

password = make_password("mudarsenha@123")


def run():
    with transaction.atomic():
        admin_group = Group.objects.create(name="Administrador")
        admin_group.permissions.set(Permission.objects.filter(codename__contains="bo_"))
        admin = AdministrativeUser.objects.create(
            username="admin",
            first_name="Admin",
            email="admin@email.com",
            profile=AdministrativeProfile.ADMIN,
            password=password,
            is_staff=True,
        )
        admin.groups.add(admin_group)

        supervisor_group = Group.objects.create(name="Supervisor")
        supervisor_group.permissions.set(
            [
                Permission.objects.get(codename="bo_can_view_affiliates"),
                Permission.objects.get(codename="bo_can_edit_affiliates"),
                Permission.objects.get(codename="bo_can_view_and_edit_managers"),
            ]
        )

        supervisor1 = AdministrativeUser.objects.create(
            username="supervisor1",
            first_name="Supervisor1",
            email="supervisor1@email.com",
            profile=AdministrativeProfile.SUPERVISOR,
            password=password,
            is_staff=True,
            parent=admin,
        )
        supervisor1.groups.add(supervisor_group)
        supervisor2 = AdministrativeUser.objects.create(
            username="supervisor2",
            first_name="Supervisor2",
            email="supervisor2@email.com",
            profile=AdministrativeProfile.SUPERVISOR,
            password=password,
            is_staff=True,
            parent=admin,
        )
        supervisor2.groups.add(supervisor_group)

        manager_group = Group.objects.create(name="Gerente")
        manager_group.permissions.set(
            [
                Permission.objects.get(codename="bo_can_view_affiliates"),
            ]
        )

        manager11 = AdministrativeUser.objects.create(
            username="manager11",
            first_name="Manager11",
            email="manager11@email.com",
            profile=AdministrativeProfile.MANAGER,
            password=password,
            is_staff=True,
            parent=supervisor1,
        )
        manager11.groups.add(manager_group)
        manager12 = AdministrativeUser.objects.create(
            username="manager12",
            first_name="Manager12",
            email="manager12@email.com",
            profile=AdministrativeProfile.MANAGER,
            password=password,
            is_staff=True,
            parent=supervisor1,
        )
        manager12.groups.add(manager_group)
        manager21 = AdministrativeUser.objects.create(
            username="manager21",
            first_name="Manager21",
            email="manager21@email.com",
            profile=AdministrativeProfile.MANAGER,
            password=password,
            is_staff=True,
            parent=supervisor2,
        )
        manager21.groups.add(manager_group)
        manager22 = AdministrativeUser.objects.create(
            username="manager22",
            first_name="Manager22",
            email="manager22@email.com",
            profile=AdministrativeProfile.MANAGER,
            password=password,
            is_staff=True,
            parent=supervisor2,
        )
        manager22.groups.add(manager_group)
        Affiliate.objects.create(
            username="affiliate111",
            first_name="Affiliate111",
            name="affiliate111",
            email="affiliate111@email.com",
            phone="123456789",
            cpf="123456789",
            user_above=manager11,
            password="mudarsenha@123"
        )

        Affiliate.objects.create(
            username="affiliate112",
            first_name="Affiliate112",
            name="affiliate112",
            email="affiliate112@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager11,
        )
        
        Affiliate.objects.create(
            username="affiliate121",
            first_name="Affiliate121",
            name="affiliate121",
            email="affiliate121@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager12,
        )
        
        Affiliate.objects.create(
            username="affiliate122",
            first_name="Affiliate122",
            name="affiliate122",
            email="affiliate122@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager12,
        )
        
        Affiliate.objects.create(
            username="affiliate211",
            first_name="Affiliate211",
            name="affiliate211",
            email="affiliate211@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager21,
        )
        
        Affiliate.objects.create(
            username="affiliate212",
            first_name="Affiliate212",
            name="affiliate212",
            email="affiliate212@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager21,
        )
        
        Affiliate.objects.create(
            username="affiliate221",
            first_name="Affiliate221",
            name="affiliate221",
            email="affiliate221@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager22,
        )
        
        Affiliate.objects.create(
            username="affiliate222",
            first_name="Affiliate222",
            name="affiliate222",
            email="affiliate222@email.com",
            phone="123456789",
            cpf=get_random_string(length=11, allowed_chars="1234567890"),
            password="mudarsenha@123",
            user_above=manager22,
        )
        