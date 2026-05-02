from __future__ import annotations

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("pricing/", views.pricing, name="pricing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.home, name="home"),
    path("customers/", views.customers, name="customers"),
    path("leads/", views.leads, name="leads"),
    path("deals/", views.deals, name="deals"),
    path("tasks/", views.tasks, name="tasks"),
]
