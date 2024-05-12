from django.contrib import admin
from django.urls import path
from django.urls.resolvers import URLResolver
from administration.admin.backoffice_admin.affiliate import AffiliateAdmin
from administration.views import AffiliateView
from ecommerce.models import Affiliate


# Register your models here.
class AdministrationSite(admin.AdminSite):
    site_header = "Jb Ecommerce Admin Portal"
    site_title = "Jb Ecommerce Admin Portal"
    index_title = "Welcome to Jb Ecommerce Admin Portal"


jb_on_administration_site = AdministrationSite(name="jb_ecommerce_admin")


jb_on_administration_site.register(Affiliate, AffiliateAdmin)
