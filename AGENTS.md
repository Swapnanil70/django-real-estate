# Django Real Estate Platform - Technical Reference & Agent Collaboration Guide

**Last Updated**: April 3, 2026  
**Django Version**: 5.2.8 | **DRF Version**: 3.16.1 | **Python**: 3.14  
**Repository**: `/Users/swapnanil-mac/Projects/Real Estate main/django-real-estate/`

---

## 1. Repository Intent

**django-real-estate** is a production-grade REST API backend powering a real estate marketplace SaaS platform. The system enables:

- **Property Management**: List, search, filter, and manage residential/commercial property listings with multi-image support
- **User Roles & Profiles**: Support for buyer, seller, and agent personas with role-based features (licensing, ratings)
- **Agent Ratings System**: Peer review mechanism for real estate professionals (1-5 star rating with comments)
- **Lead Management**: Capture and route property inquiries via email notifications
- **Media Handling**: Image upload/storage for property galleries (cover photo + 4 additional photos)
- **Search & Discovery**: Advanced filtering (price range, bedrooms, bathrooms, property type, advert type, location)
- **Async Processing**: Celery-based email delivery and background task execution
- **JWT Authentication**: Email-based login with refresh token lifecycle management

**Tech Stack**: Django 5.2.8, DRF 3.16.1, PostgreSQL 16, Redis 6, Celery 5.6.0, Nginx, Docker  
**Frontend**: React.js (separate `/client` application)  
**Deployment**: Docker Compose (local/dev), Kubernetes-ready (production)

---

## 2. Quick Navigation

### Project Structure Reference

```
django-real-estate/
├── real_estate/                 # Django project root
│   ├── settings/
│   │   ├── base.py              # Shared config (logging, JWT, Celery, auth)
│   │   ├── development.py        # Dev overrides (email, DB, Celery broker)
│   │   └── production.py         # Prod config (hardening, caching, SSL)
│   ├── urls.py                  # API versioning, endpoint routing (/api/v1/*)
│   ├── wsgi.py, asgi.py        # Application entry points
│   └── celery.py                # Celery app initialization & task discovery
│
├── apps/                        # Business logic modules (Django apps)
│   ├── users/                   # User model, auth, account management
│   ├── profiles/                # User profiles, role classification
│   ├── properties/              # Property listings, search, views tracking
│   ├── ratings/                 # Agent/property ratings & reviews
│   ├── enquiries/               # Contact form submissions
│   └── common/                  # Shared base classes (TimeStampedUUIDModel)
│
├── client/                      # React frontend (separate app)
├── docker/                      # Container definitions
├── tests/                       # pytest-django tests & factories
├── docker-compose.yml           # Multi-container orchestration
├── Makefile                     # Build automation
├── requirements.txt             # Pinned Python 3.14 dependencies
└── AGENTS.md, CLAUDE.md        # Technical reference & development guidelines
```

---

## 3. Package Index (Dependencies)

### Core Django & REST Framework
- `Django==5.2.8` – Web framework
- `djangorestframework==3.16.1` – REST API toolkit, serializers, viewsets

### Database & ORM Extensions
- `psycopg2-binary==2.9.11` – PostgreSQL adapter
- `django-countries==8.2.0` – Country field with choice lists
- `django-phonenumber-field==8.4.0` – Validated phone number field
- `phonenumbers==9.0.19` – International phone number parsing

### Authentication & Security
- `djoser==2.3.3` – User endpoints (register, login, password reset, email confirmation)
- `djangorestframework-simplejwt==5.5.1` – JWT token generation/validation
- `PyJWT==2.10.1` – JWT library

### Async Tasks & Queuing
- `celery==5.6.0` – Distributed task queue
- `redis==7.1.0` – Broker backend (also future caching)
- `django-celery-email==3.0.0` – Async email sending
- `flower==2.0.1` – Celery monitoring dashboard

### API & Utilities
- `django-filter==25.2` – QuerySet filtering on endpoints
- `django-autoslug==1.9.9` – Auto-generated URL slugs (Property.title → slug)
- `django-environ==0.12.0` – .env file loading
- `Pillow==12.0.0` – Image validation/processing
- `PyYAML==6.0.3` – YAML for schemas

### Testing & Code Quality
- `pytest-django==4.11.1` – Pytest plugin for Django
- `pytest-factoryboy==2.8.1` – Factory-boy integration
- `pytest-cov==7.0.0` – Code coverage measurement
- `Faker==38.2.0` – Synthetic test data
- `flake8==7.3.0` – PEP 8 linter
- `black==25.11.0` – Auto-formatter
- `isort==7.0.0` – Import organizer

---

## 4. Database Schema

### Core Tables

#### **users_user** (Custom User Model)
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE, API key)
    username (VARCHAR 255, UNIQUE)
    first_name, last_name (VARCHAR 50)
    email (EmailField, UNIQUE)          ← USERNAME_FIELD
    password (hashed)
    is_staff, is_active, is_superuser (BOOL)
    date_joined (DateTime)
```

#### **profiles_profile** (OneToOne with User)
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE)
    user_id (OneToOneField → users_user, CASCADE)
    phone_number (PhoneNumberField)
    about_me, license (TextField, CharField)
    profile_photo (ImageField, nullable)
    gender (CharField, choices: Male/Female/Other)
    country, city (CountryField, CharField)
    is_buyer, is_seller, is_agent, top_agent (BOOL)
    rating (DecimalField 4.2, nullable)
    num_reviews (INT)
    created_at, updated_at (DateTime)
```

#### **properties_property**
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE)
    user_id (ForeignKey → users_user)
    title (CharField 250, auto-slugs to slug)
    slug (AutoSlugField, UNIQUE)
    ref_code (CharField 255, UNIQUE random 10-char)
    description, country, city, postal_code, street_address (text fields)
    property_number, price, tax, plot_area (numeric fields)
    bedrooms, bathrooms, total_floors (numeric)
    advert_type, property_type (CharField, choices)
    cover_photo, photo1-4 (ImageField, nullable)
    published_status (BOOL)
    views (INT)
    created_at, updated_at (DateTime)
```

#### **properties_propertyviews** (View Tracking)
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE)
    ip (CharField 250)
    property_id (ForeignKey → properties_property, CASCADE)
    created_at, updated_at (DateTime)
    UNIQUE (property_id, ip)  ← One view per IP per property
```

#### **profiles_rating**
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE)
    rater_id (ForeignKey → users_user, SET_NULL)
    agent_id (ForeignKey → profiles_profile, SET_NULL)
    rating (IntegerField, choices: 1-5)
    comment (TextField, nullable)
    created_at, updated_at (DateTime)
    UNIQUE (rater_id, agent_id)  ← One rating per rater-agent pair
```

#### **enquiries_enquiry**
```
PK: pkid (BigAutoField)
    id (UUID, UNIQUE)
    name, subject (CharField)
    phone_number (PhoneNumberField)
    email (EmailField)
    message (TextField)
    created_at, updated_at (DateTime)
```

### Relationship Diagram

```
User (1) ──OneToOne── (1) Profile
  │
  ├─ ForeignKey ──── Many Property (user=agent/seller)
  │
  ├─ ForeignKey ──── Many Rating (rater=user)
  │
  └─ ??? ──── Many Enquiry

Profile (1) ──── Many Rating (agent=profile, is_agent=True)

Property (1) ──── Many PropertyViews (IP tracking, CASCADE delete)
```

---

## 5. REST API Endpoints

**Base**: `/api/v1/`

### 5.1 Authentication (via Djoser)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/auth/users/` | AllowAny | Register user + auto-create Profile + send activation email |
| POST | `/auth/users/activate/` | AllowAny | Activate account via email token |
| POST | `/auth/jwt/create/` | AllowAny | Login: email+password → {access, refresh tokens} |
| POST | `/auth/jwt/refresh/` | AllowAny | Refresh: {refresh} → {new access token} |
| POST | `/auth/jwt/verify/` | AllowAny | Verify: {access} → validity check |
| POST | `/auth/users/reset_password/` | AllowAny | Request password reset |
| POST | `/auth/users/reset_password_confirm/` | AllowAny | Confirm reset with token |
| POST | `/auth/users/set_password/` | IsAuthenticated | Change password (logged-in) |

---

### 5.2 Profiles

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/profiles/me/` | IsAuthenticated | Get logged-in user's profile |
| PATCH | `/profiles/update/<username>/` | IsAuthenticated | Update own profile (owner check) |
| GET | `/profiles/agents/all/` | IsAuthenticated | List all agents (is_agent=True) |
| GET | `/profiles/top-agents/all/` | IsAuthenticated | List top agents (top_agent=True) |

**Query Filters**: None currently; can add pagination

---

### 5.3 Properties

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/properties/all/` | AllowAny | List all properties (paginated, filtered) |
| GET | `/properties/agents/` | IsAuthenticated | List logged-in agent's properties |
| POST | `/properties/create/` | IsAuthenticated | Create property listing |
| GET | `/properties/details/<slug>/` | AllowAny | Get property details + increment view count |
| PUT | `/properties/update/<slug>/` | IsAuthenticated | Update property (owner only) |
| DELETE | `/properties/delete/<slug>/` | IsAuthenticated | Delete property (owner only) |
| POST | `/properties/search/` | AllowAny | Advanced search (form payload) |
| POST | `/properties/upload/` | IsAuthenticated | Upload images (cover_photo, photo1-4) |

**Filters on `/properties/all/` & `/properties/agents/`**:
```
?advert_type=For Sale
?property_type=House
?price=100000
?price__gt=50000
?price__lt=500000
?search=oceanview       # Searches country, city
?ordering=-created_at   # Order by field
?page=1
```

**Search Endpoint** (`POST /properties/search/`):
```json
Request Body:
{
  "advert_type": "For Sale",
  "property_type": "House",
  "price": "$100,000+",      // Predefined ranges parsed to numeric
  "bedrooms": "2+",          // Predefined ranges
  "bathrooms": "1+",
  "catch_phrase": "oceanview"
}
```

---

### 5.4 Ratings (Agent Reviews)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/ratings/<profile_id>/` | IsAuthenticated | Rate agent (1-5 stars, comment) |

**Validations**:
- 403: Self-rating
- 403: Duplicate rating (already rated)
- 400: Rating == 0
- 404: Profile not is_agent

---

### 5.5 Enquiries (Contact)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/enquiries/` | AllowAny | Submit inquiry + send email (async) |

**Request**:
```json
{
  "name": "Jane Smith",
  "phone_number": "+1234567890",
  "email": "jane@example.com",
  "subject": "...",
  "message": "..."
}
```

---

### 5.6 Property Views (Historical)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/properties/views/` | AllowAny | List all PropertyViews records (analytics) |

---

## 6. Module Integrations

### Signal-Based Auto-Creation
- **Trigger**: User created (registration or admin)
- **Effect**: Profile auto-created with defaults (gender="Other", country="KE")
- **File**: `apps/profiles/signals.py`

### Email via Celery
- **Config**: `EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"`
- **Broker**: Redis at `CELERY_BROKER` env var
- **Usage**: Any `send_mail()` call queued to Celery, processed by worker

### View Tracking
- **Trigger**: `PropertyDetailAPIView.get()` extracts client IP
- **Logic**: Creates PropertyViews(property, ip) if not exists; increments Property.views
- **Purpose**: Track property interest per IP

### Filtering & Pagination
- **Backend**: `django-filter` (DjangoFilterBackend)
- **Search**: Full-text search on country, city
- **Pagination**: `PropertyPagination` (10 items/page)

---

## 7. Classes and Functionality

### View Classes

#### **APIView Subclasses**
- **GetProfileAPIView**: GET /me/ → retrieve logged-in user profile
- **UpdateProfileAPIView**: PATCH /update/<username>/ → update own profile (ownership check)
- **PropertyDetailAPIView**: GET /details/<slug>/ → retrieve + auto-increment views

#### **ListAPIView Subclasses** (Generic Views)
- **AgentListAPIView**: GET /agents/all/ → list all agents (should filter by current user?)
- **TopAgentsListAPIView**: GET /top-agents/all/ → list top agents
- **ListAllPropertiesAPIView**: GET /all/ → list all properties (filters, search, ordering, pagination)
- **ListAgentsPropertiesAPIView**: GET /agents/ → list current agent's properties
- **PropertyViewsAPIView**: GET /views/ → list all view records
- **PropertySearchAPIView**: POST /search/ → advanced search (iterative filtering)

#### **Function-Based Views** (@api_view decorator)
- **create_property_api_view**: POST /create/ → create property (auto-slug, auto-ref_code)
- **update_property_api_view**: PUT /update/<slug>/ → update property (owner only)
- **delete_property_api_view**: DELETE /delete/<slug>/ → delete property (owner only)
- **uploadPropertyImage**: POST /upload/ → upload up to 5 images (multipart)
- **send_enquiry_email**: POST /enquiries/ → submit inquiry + email + save DB record
- **create_agent_review**: POST /ratings/<profile_id>/ → rate agent (validations)

### Serializer Classes

| Class | Model | Type | Purpose |
|-------|-------|------|---------|
| ProfileSerializer | Profile | ModelSerializer | List profiles; includes nested reviews |
| UpdateProfileSerializer | Profile | ModelSerializer | PATCH profile (selective fields) |
| PropertySerializer | Property | ModelSerializer | List/detail properties; includes nested agent |
| PropertyCreateSerializer | Property | ModelSerializer | POST create (excludes timestamps) |
| PropertyViewSerializer | PropertyViews | ModelSerializer | List views; excludes timestamps |
| RatingSerializer | Rating | ModelSerializer | Nested in ProfileSerializer.reviews |

### Exception Classes

| Exception | Status | Message | File |
|-----------|--------|---------|------|
| ProfileNotFound | 404 | "Profile doesn't exist" | profiles/exceptions.py |
| NotYourProfile | 403 | "Can't edit profile not yours" | profiles/exceptions.py |
| PropertyNotFound | 404 | "Property doesn't exist" | properties/exceptions.py |

---

## 8. Configuration Files

### settings/base.py (Shared Defaults)
```python
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(" ")
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": env("SIGNING_KEY"),
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "SERIALIZERS": { ... },
}

STATIC_URL = "/staticfiles/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

CSRF_TRUSTED_ORIGINS = ['http://localhost:9090', ...]

# Logging
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.config.dictConfig({ ... })
```

### settings/development.py (Dev Overrides)
```python
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
DEFAULT_FROM_EMAIL = "info@real_estate.com"

DATABASES = {
    "default": {
        "ENGINE": env("POSTGRES_ENGINE"),
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("PG_HOST"),
        "PORT": env("PG_PORT"),
    }
}

broker_url = env("CELERY_BROKER")         # redis://redis:6379/0
result_backend = env("CELERY_BACKEND")   # redis://redis:6379/0
timezone = "Asia/Kolkata"
```

### .env (Git-Ignored Secrets)
```bash
SECRET_KEY=<50+ random chars>
DEBUG=False
ALLOWED_HOSTS="localhost 127.0.0.1"
SIGNING_KEY=<random>
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=real_estate_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=<password>
PG_HOST=postgres-db
PG_PORT=5432
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
EMAIL_PORT=587
DOMAIN=http://localhost:8000
```

---

## 9. Build System

### Makefile Targets
```
make build            # docker compose up --build -d
make up               # docker compose up -d
make down             # docker compose down
make migrate          # Run DB migrations
make makemigrations   # Generate migration files
make test             # Run pytest with coverage
make flake8, black, isort  # Linting & formatting
```

### Docker Images
- **django**: Python 3.14 + Django + all dependencies (3-stage build)
- **postgres**: PostgreSQL 16-alpine
- **redis**: Redis 6-alpine
- **celery**: Same as django image, different entrypoint (/start-celeryworker, /start-flower)
- **nginx**: Nginx alpine, proxies to django, serves static/media

---

## 10. Startup Sequence

### Local Dev (python manage.py runserver)
1. `python3.14 -m venv .venv-py314 && source .venv-py314/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` → `.env`, add secrets
4. `python manage.py migrate` → apply schema
5. `python manage.py createsuperuser` → create admin
6. `python manage.py runserver` → Django on :8000
7. `celery -A real_estate worker -l info` (separate terminal)

### Docker Compose (make build)
1. `docker compose up --build -d`
2. Services start in dependency order:
   - postgres-db, redis (no deps)
   - api, celery-worker (after DB ready)
   - flower, nginx (after api, worker ready)
3. /start script in api container:
   - PostgreSQL readiness check
   - `python manage.py migrate --no-input`
   - `python manage.py collectstatic --no-input`
   - Start Django server
4. System ready:
   - API: http://localhost:8000
   - Nginx: http://localhost:8080
   - Flower: http://localhost:5557
   - PostgreSQL: localhost:5434

---

## 11. Code Patterns

### JWT Authentication
```python
POST /api/v1/auth/jwt/create/
  {"email": "...", "password": "..."}
  ↓
  {"access": "<token>", "refresh": "<token>"}
  
Authorization: Bearer <access_token>  # All authenticated endpoints
```

### Resource Ownership Pattern
```python
if property.user != request.user:
    return Response({"error": "..."}, status=status.HTTP_403_FORBIDDEN)
# Safe to update/delete
```

### Computed Fields
```python
class PropertySerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    def get_final_price(self, obj):
        return obj.final_property_price  # Calls @property on model
```

### Signal-Driven Auto-Creation
```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, gender="Other", country="KE")
```

### Async Email via Celery
```python
# In settings: EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
send_mail(subject, message, from_email, [recipient_list])
# Queued to Celery, processed asynchronously by worker
```

### List Filtering & Pagination
```python
class ListAllPropertiesAPIView(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ["country", "city"]
    ordering_fields = ["created_at"]
    pagination_class = PropertyPagination

# Client: /api/v1/properties/all/?price__gt=50000&city=Nairobi&search=oceanview
```

### View Increment on Detail Fetch
```python
# Extract client IP
x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

# Increment if new IP
if not PropertyViews.objects.filter(property=property, ip=ip).exists():
    PropertyViews.objects.create(property=property, ip=ip)
    property.views += 1
    property.save()
```

---

## 12. Error Codes & Sync Errors

### HTTP Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Success (GET, PUT, PATCH) | List properties, update profile |
| 201 | Created (POST) | Create property listing |
| 400 | Bad Request (validation) | Missing fields, invalid rating (0) |
| 401 | Unauthorized (no token) | Missing JWT token |
| 403 | Forbidden (no permission) | Update others' data, self-rating |
| 404 | Not Found (resource missing) | Property by slug, profile by ID |
| 500 | Server Error | Unhandled exception |

### Custom Exceptions

| Exception | Code | Message | Trigger |
|-----------|------|---------|---------|
| ProfileNotFound | 404 | "Profile doesn't exist" | GetProfileAPIView lookup fails |
| NotYourProfile | 403 | "Can't edit profile not yours" | UpdateProfileAPIView ownership check fails |
| PropertyNotFound | 404 | "Property doesn't exist" | PropertyDetailAPIView, update/delete lookup fails |

### Validation Errors (400)

| Field | Error | Example |
|-------|-------|---------|
| email | Unique violation | "User with email already exists" |
| password | Weak password | "Password too short" |
| rating | Out of range | "Rating must be 1-5, got 0" |
| country | Invalid | "Invalid country code" |
| phone_number | Invalid | "Invalid phone number format" |

### Authorization Errors (403)

| Endpoint | Scenario | Response |
|----------|----------|----------|
| PUT /update/<slug>/ | Not property owner | `{"error": "You cannot update a property that doesn't belong to you"}` |
| DELETE /delete/<slug>/ | Not property owner | `{"error": "You cannot delete a property that doesn't belong to you"}` |
| PATCH /update/<username>/ | Not profile owner | `NotYourProfile` exception |
| POST /ratings/<id>/ | Self-rating | `{"message": "You can't rate yourself"}` (403) |
| POST /ratings/<id>/ | Already rated | `{"details": "You have already rated this agent"}` (403) |
| POST /ratings/<id>/ | Rating==0 | `{"details": "Please select a rating"}` (400) |

### Silent Error Handling (Anti-Pattern)

**Enquiry endpoint** catches all exceptions, returns generic failure:
```python
try:
    send_mail(...)
    enquiry = Enquiry(...)
    enquiry.save()
    return Response({"success": "..."})
except Exception:
    return Response({"fail": "..."})  # All errors hidden
```

**Issue**: Email failure, DB error, validation error all return 500 with same message.  
**Fix**: Catch specific exceptions, return appropriate status codes (400, 503).

---

## 13. Architectural Rules

### 1. Database Design
- Every model has `pkid` (BigAutoField) + `id` (UUID) pair
- `created_at`, `updated_at` managed automatically
- Foreign keys use CASCADE (Property, Profile) or DO_NOTHING (ratings)
- Unique constraints enforce business rules (email, slug, (rater, agent))
- Indexes on high-query fields (user_id, published_status, created_at)

### 2. Authentication
- JWT-based, email-centric (not username)
- Access token: 120 min, Refresh: 1 day
- IsAuthenticated permission enforces login on modifying endpoints
- Resource owner check (property.user == request.user) for updates/deletes

### 3. API Design
- `/api/v1/` prefix; future v2 co-exists on breaking changes
- DRF serializers with nested sources + computed fields
- Standard error format: `{"field": ["error"]}` (validation) or `{"detail": "message"}` (exceptions)
- Pagination: 10 items per page; configurable on ListAPIView

### 4. Async Processing
- Redis broker (redis://redis:6379/0)
- Celery task queues (not yet used; infrastructure ready)
- Email via django-celery-email backend (automatic queueing)
- Flower monitoring dashboard (port 5557)

### 5. Media & Files
- Local filesystem storage (/app/mediafiles)
- Pillow for image validation
- Nginx serves via /mediafiles/ URL
- CDN-ready for production (configurable storage backend)

### 6. Data Integrity
- Profile auto-created on User creation (signal)
- PropertyViews deduplication by (property, ip)
- Rating uniqueness by (rater, agent)
- Cascade deletion on Property → PropertyViews

### 7. Code Organization
- Each app is bounded context (users, profiles, properties, ratings, enquiries)
- Layering: Models → Serializers → Views → URLs
- Custom exceptions in app-level `exceptions.py`
- Signals in app-level `signals.py`

### 8. Testing
- pytest-django + factory-boy
- Fixtures in conftest.py (base_user, super_user, profile)
- Factories: UserFactory, ProfileFactory (with Faker)
- Target: >80% coverage on business logic

### 9. Security
- All secrets in .env (git-ignored)
- CORS whitelist via CSRF_TRUSTED_ORIGINS
- HTTPS via Nginx (production)
- SQL injection mitigated via ORM
- Rate limiting: TBD (use django-ratelimit or DRF throttling)

### 10. Deployment
- Docker Compose for local/dev
- Kubernetes-ready for production
- Nginx reverse proxy + gunicorn/uwsgi workers
- Static files to /staticfiles (CDN in production)
- Media files to /mediafiles (object storage in production)

---

## 14. AI Collaboration Guide

### When to Use This Document

This document provides **context for LLMs** (Claude, GPT, etc.) to:
1. Generate accurate code matching project patterns
2. Debug API errors with full schema/endpoint knowledge
3. Add features with architectural alignment
4. Refactor with understanding of existing design

### Prompt Engineering Tips

**Without AGENTS.md**:
- 10,000+ tokens for context-setting
- Multiple clarification rounds
- Generic Django code needing refactoring

**With AGENTS.md Context**:
- 2,000 tokens to load context
- Direct, specific requests
- Project-aligned code ready to review
- 70-80% fewer clarification rounds

### Example Prompts

**Vague** (results in generic code):
```
Create a new endpoint to filter properties.
```

**Specific** (results in accurate code):
```
Based on AGENTS.md section 5.3 & 7 (ListAllPropertiesAPIView pattern), create a 
UserPropertiesListAPIView that lists properties by seller (new is_seller_of field). 
Use PropertyFilter, PropertyPagination, and return PropertySerializer. 
Ensure only IsAuthenticated users can list their own properties sold.
```

### Sections to Reference

- **Section 2**: Codebase structure for file locations
- **Section 4**: DB schema for correct field names/types
- **Section 5**: API endpoints for endpoint format/parameters
- **Section 7**: Classes for implementation patterns
- **Section 8**: Config for settings/environment
- **Section 11**: Code patterns for "how  to write"
- **Section 12**: Error codes for error handling
- **Section 13**: Architectural rules for "why"

---

## Conclusion

This document is a **living technical reference** for the django-real-estate platform. It consolidates:
- Repository intent & structure
- Complete API mapping (endpoints, methods, auth, validation)
- Database schema with relationships
- Code organization & patterns
- Error handling & validation rules
- Configuration & deployment

Use it to onboard developers, configure AI models, and maintain architectural consistency.

---

**Version**: 2.0 (Comprehensive Technical Reference)  
**Generated**: April 3, 2026  
**Maintained by**: Senior Engineers & AI Agents
