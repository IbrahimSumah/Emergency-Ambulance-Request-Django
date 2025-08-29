## Role-Based Navigation, Dashboards, and Workflows

This document defines how the three user roles — Patient, Paramedic, and Admin — navigate the app, what each dashboard should surface, and how role distinctions are enforced across URLs, views, and templates. It also outlines end-to-end workflows and measurable KPIs for effective dashboards.

### Roles and Permissions

- **Patient**: Create and track ambulance requests; view personal stats/history.
- **Paramedic**: View/accept pending requests; manage assigned requests; update status.
- **Admin**: Oversee all activity; assign paramedics; manage users/fleet; analytics.

Access control is enforced via decorators in `accounts.decorators` and per-view role checks in `emergency_ambulance/dashboard_views.py`.

### URL Map and Views

Existing dashboard routes are defined in `emergency_ambulance/dashboard_urls.py` and rendered by `emergency_ambulance/dashboard_views.py`:

```4:8:emergency_ambulance/dashboard_urls.py
urlpatterns = [
    path('patient/', dashboard_views.patient_dashboard, name='patient_dashboard'),
    path('paramedic/', dashboard_views.paramedic_dashboard, name='paramedic_dashboard'),
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
]
```

Templates:
- Patient: `templates/dashboard/patient_dashboard.html`
- Paramedic: `templates/dashboard/paramedic_dashboard.html`
- Admin: `templates/dashboard/admin_dashboard.html`

These are decorated with role guards:

```40:48:emergency_ambulance/dashboard_views.py
@login_required
@paramedic_required
def paramedic_dashboard(request):
    ...
```

### Navigation Bar Behavior

The shared navbar should live in `templates/base.html` and display role-appropriate links after login. Use the authenticated `request.user.role` to drive visibility.

- **Common (authenticated)**:
  - Dashboard (role-directed): `/dashboard/` → redirects to role dashboard
  - Profile: `/accounts/profile/`
  - Logout
- **Patient-only**:
  - Create Request: `/ambulance/requests/new/`
  - My Requests: `/ambulance/requests/`
- **Paramedic-only**:
  - Assigned to Me: `/ambulance/requests/assigned/`
  - Pending Queue: `/ambulance/requests/pending/` (show badge count)
- **Admin-only**:
  - Requests: `/admin/requests/`
  - Users: `/admin/users/`
  - Ambulances: `/admin/ambulances/`
  - Analytics: `/dashboard/admin/`

Implementation notes:
- Highlight active link using `request.path`.
- Show numeric badges for pending requests and assigned items with lightweight counts in a context processor or per-view.
- Hide links the user cannot access; never rely on hiding alone — enforce on the server.

### Dashboard Composition and KPIs

Each dashboard should be composed of quick-glance KPIs, recent activity lists, and primary actions.

- **Patient Dashboard** (`patient_dashboard.html`)
  - KPIs: Total Requests, Pending, Active (Assigned/En Route/Arrived), Completed
  - Cards/List: Last 5 requests with status chips and timestamps
  - Primary actions: Create Request, View All Requests
  - Helpful info: Saved locations, emergency contacts (optional scope)

- **Paramedic Dashboard** (`paramedic_dashboard.html`)
  - KPIs: Assigned to Me (active), Completed by Me, Pending Queue, Total Handled
  - Lists: Recent Assigned (5), Recent Pending (5) with quick Accept/Decline actions
  - Primary actions: Toggle Availability, View Map (optional), Update Status
  - Map/GPS (future): Show patient pickup location if available

- **Admin Dashboard** (`admin_dashboard.html`)
  - KPIs: Total Requests, Pending, Active, Completed, Cancelled
  - Workforce: Total Users, Patients, Paramedics, Available Paramedics
  - Fleet: Total Ambulances, Available Ambulances
  - Distributions: Priority and Status charts
  - Lists: Recent Requests (10), Recent Users (5)
  - Primary actions: Assign Paramedic, Manage Users, Manage Fleet, View Analytics

Suggested visualizations:
- Mini cards with trend indicators (7d deltas if available)
- Simple bar/pie charts for priority/status distributions (client-side chart lib)

### Request Lifecycle and Workflows

Statuses from `settings.py` (`AMBULANCE_REQUEST_STATUSES`): `pending`, `assigned`, `en_route`, `arrived`, `completed`, `cancelled`.

1) Patient creates a request
- Patient → Create Request form → submits with location/priority → status `pending`.
- Patient sees it in My Requests and on dashboard Recent Requests.

2) Admin assigns a paramedic (or paramedic self-accepts when enabled)
- Admin view → select request → Assign Paramedic action → status `assigned` and `paramedic` set.
- Alternatively, Paramedic accepts from Pending Queue → status `assigned` to that paramedic.

3) Paramedic progresses the request
- Update to `en_route` when departing.
- Update to `arrived` on site.
- Update to `completed` after transport/service.

4) Cancellation
- Patient/Admin may cancel before `completed` → set `cancelled` with reason.

Role-specific constraints:
- Patient can edit/cancel only own requests and only before completion.
- Paramedic can update only requests assigned to them.
- Admin can update any request and reassign as needed.

### Template Architecture and Reuse

- `templates/base.html`: global shell and navbar; include role-aware blocks:
  - `{% block sidebar %}` optional for Admin/Paramedic extended menus
  - `{% block content %}` for dashboard/body
- `templates/dashboard/_kpi_card.html`: small KPI component partial
- `templates/dashboard/_request_row.html`: reusable row for requests list
- Use inclusion tags or simple template includes to keep views thin.

### Navigation Implementation Notes

Add a context processor to expose quick counts for navbar badges:
- Pending requests count for paramedics
- Assigned active count for paramedics
- Patient pending/active counts

Alternatively, compute counts in each view and pass to templates if global load is a concern.

### API and Mobile Integration

The REST API mirrors core operations for mobile apps (`api/` app):
- Patients: create/list requests, track status
- Paramedics: list pending/assigned, accept, update status
- Admin: dashboard stats endpoints, recent requests/users

Use token authentication for mobile clients; session auth for web.

### Security and Distinct Roles

- Enforce permissions server-side using decorators and query scoping (e.g., `AmbulanceRequest.objects.filter(patient=request.user)` for patients).
- Never leak cross-role data in list/detail views; perform explicit ownership checks.
- Hide unauthorized nav links, but always validate on the backend.

### Effectiveness Metrics (KPIs to track)

- Patient:
  - Time from request creation → assignment
  - Time from assignment → arrival
  - Completion rate; cancellations rate

- Paramedic:
  - Average response time (accept → arrival)
  - Active load (concurrent in-progress)
  - Completion volume per day/week

- Admin:
  - Pending queue size over time
  - Utilization: available paramedics vs. active requests
  - SLA adherence: thresholds for response/arrival times

### Future Scope

- Real-time updates via WebSockets for status changes and queue updates
- Geofencing and routing estimations
- Shift management and automatic assignment
- Notifications (email/SMS/push)


