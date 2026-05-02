"""Seed demo data: super admin, plans, a tenant, sample CRM records."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.billing.models import Plan
from apps.core.context import set_active_tenant
from apps.customers.models import Company, Contact
from apps.deals.models import Deal, Pipeline, Stage
from apps.leads.models import Lead, LeadSource, LeadStatus
from apps.rbac.models import Role
from apps.rbac.seed import ensure_system_roles
from apps.tasks.models import Task
from apps.tenants.models import Membership, Tenant

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for local development."

    def handle(self, *args, **options) -> None:
        ensure_system_roles()
        self._seed_plans()
        admin = self._seed_super_admin()
        tenant = self._seed_tenant(admin)
        set_active_tenant(tenant)
        try:
            self._seed_pipeline_and_deals(tenant, admin)
            self._seed_customers(tenant, admin)
            self._seed_leads(tenant, admin)
            self._seed_tasks(tenant, admin)
        finally:
            set_active_tenant(None)
        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write("Admin login: admin@novacrm.local / admin1234")

    # --- helpers -----------------------------------------------------------

    def _seed_plans(self) -> None:
        plans = [
            ("free", "Free", "For tinkerers and side projects", 0, 0, 3, 200),
            ("starter", "Starter", "For small teams getting started", 19, 190, 10, 5000),
            ("pro", "Pro", "For growing sales teams", 49, 490, 50, 50000),
            (
                "enterprise",
                "Enterprise",
                "For large orgs needing SSO + SLAs",
                199,
                1990,
                None,
                None,
            ),
        ]
        for code, name, desc, mo, yr, mu, mc in plans:
            Plan.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "price_monthly": mo,
                    "price_yearly": yr,
                    "max_users": mu,
                    "max_contacts": mc,
                    "is_active": True,
                },
            )

    def _seed_super_admin(self) -> User:
        admin, created = User.objects.get_or_create(
            email="admin@novacrm.local",
            defaults={"full_name": "Super Admin", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin1234")
            admin.email_verified_at = timezone.now()
            admin.save()
        return admin

    def _seed_tenant(self, admin) -> Tenant:
        tenant, created = Tenant.objects.get_or_create(
            slug="acme",
            defaults={
                "name": "Acme Inc.",
                "owner": admin,
                "trial_ends_at": timezone.now() + timedelta(days=30),
            },
        )
        owner_role = Role.objects.get(slug="tenant_owner", tenant__isnull=True)
        Membership.objects.get_or_create(
            user=admin,
            tenant=tenant,
            defaults={"role": owner_role, "is_default": True},
        )
        return tenant

    def _seed_pipeline_and_deals(self, tenant, admin) -> None:
        pipeline, _ = Pipeline.all_tenants.get_or_create(
            tenant=tenant, name="Sales", defaults={"is_default": True}
        )
        stages_def = [
            ("Qualification", 10, False, False),
            ("Discovery", 25, False, False),
            ("Proposal", 50, False, False),
            ("Negotiation", 75, False, False),
            ("Closed Won", 100, True, False),
            ("Closed Lost", 0, False, True),
        ]
        for i, (name, prob, won, lost) in enumerate(stages_def):
            Stage.all_tenants.update_or_create(
                tenant=tenant,
                pipeline=pipeline,
                name=name,
                defaults={"position": i, "probability": prob, "is_won": won, "is_lost": lost},
            )
        first_stage = pipeline.stages.order_by("position").first()
        for i, title in enumerate(
            ["Beta deal — Globex", "Renewal — Initech", "New logo — Soylent"]
        ):
            Deal.all_tenants.update_or_create(
                tenant=tenant,
                title=title,
                defaults={
                    "pipeline": pipeline,
                    "stage": first_stage,
                    "owner": admin,
                    "amount": 5000 * (i + 1),
                    "probability": 25,
                    "currency": "USD",
                },
            )

    def _seed_customers(self, tenant, admin) -> None:
        for name in ["Globex", "Initech", "Soylent", "Hooli", "Pied Piper"]:
            Company.all_tenants.update_or_create(
                tenant=tenant,
                name=name,
                defaults={"industry": "Software", "size": "mid", "owner": admin},
            )
        globex = Company.all_tenants.get(tenant=tenant, name="Globex")
        for first, last, email, title in [
            ("Hank", "Scorpio", "hank@globex.test", "CEO"),
            ("Mindy", "Simmons", "mindy@globex.test", "VP Sales"),
        ]:
            Contact.all_tenants.update_or_create(
                tenant=tenant,
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "title": title,
                    "company": globex,
                    "owner": admin,
                },
            )

    def _seed_leads(self, tenant, admin) -> None:
        for i in range(5):
            Lead.all_tenants.update_or_create(
                tenant=tenant,
                email=f"lead{i}@prospect.test",
                defaults={
                    "name": f"Lead {i}",
                    "phone": f"+1-555-010{i}",
                    "company_name": f"Prospect {i}",
                    "source": LeadSource.WEBSITE,
                    "status": LeadStatus.NEW,
                    "owner": admin,
                    "score": 50 + i,
                },
            )

    def _seed_tasks(self, tenant, admin) -> None:
        for title, prio in [
            ("Follow up with Globex", "high"),
            ("Prepare Initech renewal proposal", "normal"),
            ("Send Pied Piper case study", "low"),
        ]:
            Task.all_tenants.update_or_create(
                tenant=tenant,
                title=title,
                defaults={
                    "owner": admin,
                    "assignee": admin,
                    "priority": prio,
                    "due_at": timezone.now() + timedelta(days=3),
                },
            )
