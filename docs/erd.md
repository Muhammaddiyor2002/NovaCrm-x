# NovaCRM X — ERD

All tenant-owned tables share the columns:

```
id            uuid       PK     default uuid4
tenant_id     uuid       FK -> tenants_tenant.id   (indexed, NOT NULL)
created_at    timestamptz       default now()
updated_at    timestamptz       auto-updated
deleted_at    timestamptz       nullable (soft delete)
```

Plus model-specific fields described below.

## accounts.User (NOT tenant-owned — global)

| Column            | Type         | Notes                                |
| ----------------- | ------------ | ------------------------------------ |
| id                | uuid PK      |                                      |
| email             | citext UNIQUE | login identifier                    |
| full_name         | varchar(150) |                                      |
| password          | varchar(128) | argon2-hashed                        |
| is_active         | bool         |                                      |
| is_staff          | bool         |                                      |
| is_superuser      | bool         |                                      |
| email_verified_at | timestamptz  | nullable                             |
| mfa_enabled       | bool         |                                      |
| mfa_secret        | bytea        | encrypted, nullable                  |
| date_joined       | timestamptz  |                                      |
| last_login        | timestamptz  | nullable                             |

## tenants.Tenant

| Column        | Type          | Notes                              |
| ------------- | ------------- | ---------------------------------- |
| id            | uuid PK       |                                    |
| slug          | varchar(64) UNIQUE | URL slug                       |
| name          | varchar(120)  |                                    |
| owner_id      | FK User       | tenant owner                       |
| plan_id       | FK billing.Plan | nullable until selected          |
| stripe_customer_id | varchar  | nullable                           |
| trial_ends_at | timestamptz   | nullable                           |
| status        | varchar(32)   | active / suspended / archived      |

## tenants.Membership

| Column     | Type         | Notes                            |
| ---------- | ------------ | -------------------------------- |
| user_id    | FK User      |                                  |
| tenant_id  | FK Tenant    |                                  |
| role_id    | FK rbac.Role |                                  |
| invited_by | FK User      | nullable                         |

UNIQUE(user_id, tenant_id)

## rbac.Role / rbac.Permission

`Role` is per-tenant (system roles use a sentinel `tenant_id = NULL`):

| Role.name        | Permission code examples                                      |
| ---------------- | ------------------------------------------------------------- |
| super_admin      | `*`                                                           |
| tenant_owner     | `tenant.manage`, `billing.manage`, `members.manage`           |
| manager          | `customers.*`, `leads.*`, `deals.*`, `tasks.*`, `tickets.*`   |
| sales_rep        | `customers.view`, `leads.*`, `deals.*`, `tasks.*`             |
| support_agent    | `customers.view`, `tickets.*`, `notes.*`                      |
| accountant       | `billing.*`, `invoices.*`                                     |
| read_only        | `*.view`                                                      |

## customers.Company

| Column     | Type     | Notes                  |
| ---------- | -------- | ---------------------- |
| name       | varchar  | indexed                |
| website    | varchar  | nullable               |
| industry   | varchar  | nullable               |
| size       | varchar  | smb/mid/enterprise/... |
| annual_revenue | numeric | nullable           |
| address    | jsonb    | nullable               |

## customers.Contact

| Column     | Type            | Notes                             |
| ---------- | --------------- | --------------------------------- |
| company_id | FK Company      | nullable                          |
| first_name | varchar         |                                   |
| last_name  | varchar         |                                   |
| email      | citext          | indexed                           |
| phone      | varchar         | nullable                          |
| title      | varchar         | nullable                          |
| owner_id   | FK User         | indexed                           |
| tags       | array<varchar>  |                                   |

## leads.Lead

| Column      | Type        | Notes                              |
| ----------- | ----------- | ---------------------------------- |
| name        | varchar     |                                    |
| email       | citext      | indexed                            |
| phone       | varchar     | nullable                           |
| source      | varchar     | website/import/api/manual          |
| status      | varchar     | new/working/qualified/disqualified |
| score       | int         | 0-100, default 0                   |
| owner_id    | FK User     |                                    |
| converted_contact_id | FK Contact | nullable                  |
| converted_deal_id    | FK Deal    | nullable                  |

## deals.Pipeline / Stage / Deal

`Pipeline` is per-tenant; `Stage` is ordered within a pipeline.

| Deal column      | Type            | Notes                            |
| ---------------- | --------------- | -------------------------------- |
| pipeline_id      | FK Pipeline     |                                  |
| stage_id         | FK Stage        |                                  |
| title            | varchar         |                                  |
| company_id       | FK Company      | nullable                         |
| primary_contact_id | FK Contact    | nullable                         |
| owner_id         | FK User         |                                  |
| amount           | numeric(14,2)   |                                  |
| currency         | char(3)         | default tenant currency          |
| probability      | smallint        | 0-100                            |
| expected_close_date | date         | nullable                         |
| closed_at        | timestamptz     | nullable                         |
| status           | varchar         | open / won / lost                |
| lost_reason      | varchar         | nullable                         |

## tasks.Task

| Column      | Type        | Notes                              |
| ----------- | ----------- | ---------------------------------- |
| title       | varchar     |                                    |
| description | text        | nullable                           |
| due_at      | timestamptz | nullable, indexed                  |
| owner_id    | FK User     |                                    |
| assignee_id | FK User     | nullable                           |
| status      | varchar     | open/in_progress/done/cancelled    |
| priority    | varchar     | low/normal/high/urgent             |
| related_to  | generic FK  | (Contact, Company, Lead, Deal, Ticket) |

## tickets.Ticket

| Column       | Type        | Notes                              |
| ------------ | ----------- | ---------------------------------- |
| subject      | varchar     |                                    |
| body         | text        |                                    |
| contact_id   | FK Contact  | nullable                           |
| assignee_id  | FK User     | nullable                           |
| status       | varchar     | new/open/pending/resolved/closed   |
| priority     | varchar     | low/normal/high/urgent             |
| sla_due_at   | timestamptz | nullable                           |
| resolved_at  | timestamptz | nullable                           |

## billing.Plan / Subscription / Invoice

| Plan column     | Type     | Notes                                |
| --------------- | -------- | ------------------------------------ |
| code            | varchar UNIQUE | free/starter/pro/enterprise   |
| name            | varchar  |                                      |
| price_monthly   | numeric  |                                      |
| price_yearly    | numeric  |                                      |
| max_users       | int      | nullable means unlimited             |
| max_contacts    | int      | nullable means unlimited             |
| features        | jsonb    | flags                                |
| stripe_price_id_monthly | varchar | nullable                    |
| stripe_price_id_yearly  | varchar | nullable                    |

## notifications.Notification

| Column       | Type        | Notes                            |
| ------------ | ----------- | -------------------------------- |
| recipient_id | FK User     |                                  |
| level        | varchar     | info/success/warning/error       |
| verb         | varchar     | created/updated/assigned/...     |
| target       | generic FK  | nullable                         |
| message      | text        |                                  |
| read_at      | timestamptz | nullable                         |

## audit.AuditLog

| Column     | Type        | Notes                                  |
| ---------- | ----------- | -------------------------------------- |
| actor_id   | FK User     | nullable (system actions)              |
| action     | varchar     | created/updated/deleted/restored       |
| target     | generic FK  |                                        |
| changes    | jsonb       | field-level diff                       |
| ip_address | inet        | nullable                               |
| user_agent | varchar     | nullable                               |

## core.Note

Generic notes attachable to any model via GFK.

| Column     | Type        | Notes                                  |
| ---------- | ----------- | -------------------------------------- |
| author_id  | FK User     |                                        |
| target     | generic FK  | (Contact, Company, Lead, Deal, Ticket) |
| body       | text        |                                        |
