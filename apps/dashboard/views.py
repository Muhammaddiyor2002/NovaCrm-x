"""Server-rendered HTMX dashboard."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.models import User
from apps.customers.models import Company, Contact
from apps.deals.models import Deal, Pipeline, Stage
from apps.leads.models import Lead
from apps.tasks.models import Task
from apps.tenants.services import bootstrap_tenant_for_user
from apps.tickets.models import Ticket


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/landing.html")


def pricing(request: HttpRequest) -> HttpResponse:
    from apps.billing.models import Plan

    plans = Plan.objects.filter(is_active=True)
    return render(request, "dashboard/pricing.html", {"plans": plans})


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user is None:
            # Allow login with email via Django's default backend.
            user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard:home")
        messages.error(request, "Invalid credentials.")
    return render(request, "dashboard/login.html")


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        full_name = request.POST.get("full_name", "").strip()
        password = request.POST.get("password", "")
        tenant_name = request.POST.get("tenant_name", "").strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        else:
            user = User.objects.create_user(email=email, password=password, full_name=full_name)
            bootstrap_tenant_for_user(
                user=user, tenant_name=tenant_name or f"{user.get_short_name()}'s Workspace"
            )
            login(request, user)
            return redirect("dashboard:home")
    return render(request, "dashboard/register.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("dashboard:landing")


@login_required
def home(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        # User has no membership yet; bootstrap one.
        from apps.tenants.services import bootstrap_tenant_for_user

        bootstrap_tenant_for_user(
            user=request.user, tenant_name=f"{request.user.get_short_name()}'s Workspace"
        )
        return HttpResponseRedirect(request.path)

    metrics = {
        "leads_total": Lead.objects.count(),
        "leads_open": Lead.objects.exclude(status__in=["disqualified", "converted"]).count(),
        "deals_open": Deal.objects.filter(status="open").count(),
        "deals_value": Deal.objects.filter(status="open").aggregate(s=Sum("amount"))["s"] or 0,
        "tasks_today": Task.objects.filter(status__in=["open", "in_progress"]).count(),
        "tickets_open": Ticket.objects.exclude(status__in=["resolved", "closed"]).count(),
        "contacts_total": Contact.objects.count(),
        "companies_total": Company.objects.count(),
    }
    deals_by_stage = list(
        Deal.objects.filter(status="open")
        .values("stage__name")
        .annotate(count=Count("id"), value=Sum("amount"))
        .order_by("stage__position")
    )
    return render(
        request,
        "dashboard/home.html",
        {"metrics": metrics, "deals_by_stage": deals_by_stage, "active_tenant": tenant},
    )


@login_required
def customers(request: HttpRequest) -> HttpResponse:
    contacts = Contact.objects.select_related("company").order_by("-created_at")[:200]
    companies = Company.objects.order_by("-created_at")[:200]
    return render(
        request,
        "dashboard/customers.html",
        {
            "contacts": contacts,
            "companies": companies,
        },
    )


@login_required
def leads(request: HttpRequest) -> HttpResponse:
    leads_qs = Lead.objects.order_by("-score", "-created_at")[:200]
    return render(request, "dashboard/leads.html", {"leads": leads_qs})


@login_required
def deals(request: HttpRequest) -> HttpResponse:
    pipeline = Pipeline.objects.filter(is_default=True).first() or Pipeline.objects.first()
    stages: list[Stage] = []
    if pipeline:
        stages = list(pipeline.stages.order_by("position"))
        deals_by_stage_id = {}
        for stage in stages:
            deals_by_stage_id[stage.id] = list(
                Deal.objects.filter(stage=stage, status="open").select_related("primary_contact")
            )
    else:
        deals_by_stage_id = {}
    columns = [(s, deals_by_stage_id.get(s.id, [])) for s in stages]
    return render(request, "dashboard/deals.html", {"pipeline": pipeline, "columns": columns})


@login_required
def tasks(request: HttpRequest) -> HttpResponse:
    tasks_qs = Task.objects.order_by("status", "due_at", "-created_at")[:200]
    return render(request, "dashboard/tasks.html", {"tasks": tasks_qs})
