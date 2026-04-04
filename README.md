# Django Real Estate Platform - Complete Technical Documentation

**Version**: 2.0 | **Django**: 5.2.8 | **DRF**: 3.16.1 | **Python**: 3.14 | **Status**: Production-Ready

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Application Flow Diagrams](#application-flow-diagrams)
5. [Business Logic & Workflows](#business-logic--workflows)
6. [Setup & Installation](#setup--installation)
7. [Project Structure](#project-structure)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Database Schema](#database-schema)
10. [Development Guidelines](#development-guidelines)

---

## 🏠 Project Overview

**Django Real Estate Platform** is a production-grade REST API backend powering a SaaS real estate marketplace. It enables:

- **Property Management**: List, search, filter, and manage residential/commercial properties with multi-image support
- **User Roles & Profiles**: Support for buyer, seller, and agent personas with role-based features (licensing, ratings)
- **Agent Ratings System**: Peer review mechanism for real estate professionals (1-5 star rating with comments)
- **Lead Management**: Capture and route property inquiries via email notifications
- **Media Handling**: Image upload/storage for property galleries (cover photo + 4 additional photos)
- **Search & Discovery**: Advanced filtering (price range, bedrooms, bathrooms, property type, location)
- **Async Processing**: Celery-based email delivery and background task execution
- **JWT Authentication**: Email-based login with refresh token lifecycle management

### Key Features

✅ **Multi-role support** (Buyer, Seller, Agent)  
✅ **Advanced property search** with 6+ filter dimensions  
✅ **Real-time view tracking** with IP deduplication  
✅ **Asynchronous email notifications** via Celery + Redis  
✅ **Signal-based auto-relationships** (Profile auto-creation)  
✅ **Computed fields** (final property price = price + tax)  
✅ **Pagination & filtering** on all list endpoints  
✅ **Resource ownership validation** (no unauthorized updates/deletes)  

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | Django | 5.2.8 | REST API framework |
| REST API | Django REST Framework | 3.16.1 | Serializers, viewsets, permissions |
| Authentication | djoser + JWT | 2.3.3, 5.5.1 | User auth, email-based login |
| Database | PostgreSQL | 16-alpine | Relational database |
| Message Queue | Redis | 6-alpine | Celery broker |
| Async Tasks | Celery | 5.6.0 | Background email, scheduled tasks |
| Task Monitoring | Flower | 2.1.1 | Web UI for Celery tasks |
| Image Processing | Pillow | 12.0.0 | Image validation |
| Filtering | django-filter | 25.2 | Advanced query filtering |
| CORS | django-cors-headers | 4.3.1 | Cross-origin requests |

### Frontend
| Component | Technology |
|-----------|-----------|
| UI Framework | React.js |
| State Management | Redux |
| HTTP Client | Axios (via Redux) |
| Deployment | Docker, Nginx |

### DevOps & Infrastructure
| Component | Technology | Version |
|-----------|-----------|---------|
| Containerization | Docker | Latest |
| Orchestration | Docker Compose | 3.8+ |
| Web Server | Nginx | Alpine |
| App Server | Gunicorn | Latest |
| Python Runtime | Python | 3.14 |

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (React.js)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Auth Pages   │  │ Property List│  │ Agent Rating Page    │  │
│  │ (Login/Reg)  │  │ & Detail     │  │ & Profile            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTPS / REST API
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│                    NGINX Reverse Proxy (Port 80)                  │
│              Routes requests to API (port 8000)                   │
└────────────────────────┬──────────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│              Django REST API (port 8000)                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ API Endpoints (/api/v1/)                                    │ │
│  │  • /auth/ (user registration, login, password reset)        │ │
│  │  • /profile/ (user profiles, agents list, top agents)       │ │
│  │  • /properties/ (list, create, detail, update, delete)      │ │
│  │  • /properties/search/ (advanced search with filters)       │ │
│  │  • /properties/upload/ (multipart image upload)             │ │
│  │  • /ratings/ (agent reviews)                                │ │
│  │  • /enquiries/ (contact form submissions)                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                         │                                         │
│        ┌────────────────┼────────────────┐                       │
│        │                │                │                       │
│        ▼                ▼                ▼                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Models   │  │ Serializers  │  │ Views/Logic  │              │
│  │ (6 types)│  │ (7 total)    │  │ (15 classes) │              │
│  └──────────┘  └──────────────┘  └──────────────┘              │
│        │                │                │                       │
│        └────────────────┼────────────────┘                       │
│                         │                                         │
└────────────────────────┬──────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │PostgreSQL│   │  Redis   │   │Celery    │
    │ Database │   │ (Broker) │   │ Worker   │
    │ (Port    │   │(Port 6379)   │(Async    │
    │ 5432)    │   │         │   │Tasks)    │
    └─────────┘   └──────────┘   └──────────┘
         │            Task Queue      │
         └─────────────┬──────────────┘
                       │
              ┌────────▼────────┐
              │ Celery Tasks:   │
              │ • send_email    │
              │ • async jobs    │
              └─────────────────┘
```

### Container Architecture (Docker Compose)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Docker Compose (8 Services)                  │
├─────────────┬──────────────┬──────────────┬─────────────────────┤
│   API       │  PostgreSQL  │    Redis     │   Celery Worker     │
│ (Django)    │   (Port      │   (Port      │   (Async Tasks)     │
│ (Port 8000) │   5432)      │   6379)      │                     │
├─────────────┼──────────────┼──────────────┼─────────────────────┤
│  Flower     │   Nginx      │    Client    │   Celery Beat       │
│ (Monitor)   │  (Proxy)     │   (React)    │  (Periodic Tasks)   │
│ (Port 5557) │  (Port 80)   │  (Port 3000) │   (Optional)        │
└─────────────┴──────────────┴──────────────┴─────────────────────┘
```

---

## 📊 Application Flow Diagrams

### 1️⃣ User Registration & Authentication Flow

```
┌────────────────┐
│ User Registers │
│ (Client)       │
└────────┬───────┘
         │ POST /api/v1/auth/users/
         │ { email, password, first_name, last_name }
         ▼
    ┌─────────────────────────┐
    │ CustomUserManager       │
    │ .create_user()          │
    │ • Validate email        │
    │ • Hash password         │
    │ • Save to PostgreSQL    │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Signal Trigger          │
    │ post_save(User)         │
    │ auto-creates Profile    │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Send Activation Email   │
    │ (via Celery/async)      │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ User Activates Email    │
    │ (click link)            │
    │ POST /auth/users/       │
    │ activate/               │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ User Logs In            │
    │ POST /auth/jwt/create/  │
    │ { email, password }     │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Return JWT Tokens       │
    │ • access_token (120min) │
    │ • refresh_token (1 day) │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Client Stores Tokens    │
    │ (localStorage/Redux)    │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Future Requests:        │
    │ Authorization: Bearer   │
    │ <access_token>          │
    └─────────────────────────┘
```

### 2️⃣ Property Listing & Search Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    AGENT LISTS PROPERTY                       │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ POST /api/v1/properties/create/                              │
│ {title, description, price, bedrooms, photo_urls, ...}      │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ PropertyCreateSerializer Validation                           │
│ • Check user is_agent=True                                   │
│ • Validate price > 0                                         │
│ • Generate slug & ref_code                                   │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ Save to PostgreSQL                                            │
│ Properties table:                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ id (UUID) | title | slug | price | tax | final_price  │ │
│ │ (computed: price + tax) | bedrooms | bathrooms | ...   │ │
│ └─────────────────────────────────────────────────────────┘ │
│ Default: published_status = False (unpublished)              │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ BUYER SEARCHES FOR PROPERTIES                                 │
└──────────┬───────────────────────────────────────────────────┘
           │
           ├─ Option 1: Browse All Published Properties
           │  GET /api/v1/properties/all/
           │  Response: Paginated list (10 per page)
           │
           ├─ Option 2: Filter by Criteria
           │  GET /api/v1/properties/all/?
           │      advert_type=For Sale
           │      &property_type=House
           │      &price__gte=41,50,000
           │      &bedrooms__gte=2
           │      &search=oceanview
           │
           └─ Option 3: Advanced Search
              POST /api/v1/properties/search/
              {
                "advert_type": "For Sale",
                "property_type": "House",
                "price": "₹41,50,000+",
                "bedrooms": "2+",
                "bathrooms": "1+",
                "catch_phrase": "oceanview"
              }
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ ListAllPropertiesAPIView / PropertySearchAPIView             │
│ • Apply DjangoFilterBackend filters                          │
│ • Apply SearchFilter (country, city)                         │
│ • Apply OrderingFilter (created_at, price)                   │
│ • Return paginated results                                    │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ BUYER CLICKS PROPERTY TO VIEW DETAILS                         │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ GET /api/v1/properties/details/<slug>/                       │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ PropertyDetailAPIView.get()                                   │
│ • Extract client IP (from X-Forwarded-For or REMOTE_ADDR)    │
│ • Check if IP already viewed this property                    │
│ • If NEW IP: Create PropertyViews(property, ip) record        │
│ • If NEW IP: Increment property.views counter                │
│ • Return PropertySerializer with nested agent info           │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│ PropertyViews Table (View Tracking)                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ property_id | ip_address | created_at                  │ │
│ │ Unique constraint: (property_id, ip_address)            │ │
│ │ Purpose: Prevent duplicate view counts from same IP     │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 3️⃣ Advanced Property Search Flow (Detailed)

```
CLIENT REQUEST:
┌──────────────────────────────────────────────────────┐
│ POST /api/v1/properties/search/                      │
│ {                                                     │
│   "advert_type": "For Sale",                         │
│   "property_type": "House",                          │
│   "price": "₹41,50,000+",                            │
│   "bedrooms": "2+",                                  │
│   "bathrooms": "1+",                                 │
│   "catch_phrase": "oceanview"                        │
│ }                                                     │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ PropertySearchAPIView.post()                         │
│                                                      │
│ Step 1: Base Queryset                               │
│ queryset = Property.objects.filter(                │
│   published_status=True  ← Only published           │
│ )                                                    │
│                                                      │
│ Step 2: Filter by Advert Type                       │
│ if "advert_type" in data:                           │
│   advert_type = data["advert_type"]                 │
│   queryset.filter(advert_type__iexact=advert_type)  │
│   ↓ Results: For Sale, For Rent, Auction            │
│                                                      │
│ Step 3: Filter by Property Type                     │
│ if "property_type" in data:                         │
│   property_type = data["property_type"]             │
│   queryset.filter(property_type__iexact=property)   │
│   ↓ Results: House, Apartment, Office, etc.         │
│                                                      │
│ Step 4: Filter by Price Range (INR)                 │
│ price_map = {                                       │
│   "₹0+": 0,                                         │
│   "₹41,50,000+": 4150000,                           │
│   "₹83,00,000+": 8300000,                           │
│   "₹1,66,00,000+": 16600000,                        │
│   "₹41,50,00,000+": 415000000,                      │
│   "₹49,80,00,000+": 49800000,                       │
│   "Any": -1                                         │
│ }                                                    │
│ price_value = price_map.get(price, -1)             │
│ if price_value != -1:                               │
│   queryset.filter(price__gte=price_value)           │
│   ↓ Results: price >= 41,50,000                     │
│                                                      │
│ Step 5: Filter by Bedrooms                          │
│ bedroom_map = {"0+": 0, "1+": 1, "2+": 2, ...}     │
│ queryset.filter(bedrooms__gte=bedroom_value)        │
│ ↓ Results: bedrooms >= 2                            │
│                                                      │
│ Step 6: Filter by Bathrooms                         │
│ bathroom_map = {"0+": 0.0, "1+": 1.0, ...}        │
│ queryset.filter(bathrooms__gte=bathroom_value)      │
│ ↓ Results: bathrooms >= 1.0                         │
│                                                      │
│ Step 7: Search in Description                       │
│ if catch_phrase:                                    │
│   queryset.filter(description__icontains=phrase)    │
│   ↓ Results: "oceanview" in description             │
│                                                      │
│ Step 8: Serialize & Return                          │
│ serializer = PropertySerializer(queryset, many=True)│
│ return Response(data)                               │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ DATABASE QUERY EXECUTION                            │
│ SELECT * FROM properties                            │
│ WHERE published_status = true                       │
│   AND advert_type ILIKE 'For Sale'                  │
│   AND property_type ILIKE 'House'                   │
│   AND price >= 4150000                              │
│   AND bedrooms >= 2                                 │
│   AND bathrooms >= 1.0                              │
│   AND description ILIKE '%oceanview%'               │
│ ORDER BY created_at DESC                            │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ RESPONSE TO CLIENT (JSON)                           │
│ {                                                    │
│   "count": 5,                                       │
│   "next": null,                                     │
│   "previous": null,                                 │
│   "results": [                                      │
│     {                                               │
│       "id": "uuid-1",                               │
│       "title": "Oceanview House",                   │
│       "price": 5000000,                             │
│       "tax": 750000,                                │
│       "final_property_price": 5750000,              │
│       "bedrooms": 3,                                │
│       "bathrooms": 2,                               │
│       "description": "Beautiful oceanview...",      │
│       "cover_photo": "/mediafiles/cover.jpg",       │
│       "user": "agent_username",                     │
│       "views": 42                                   │
│     },                                              │
│     ... (4 more properties)                         │
│   ]                                                 │
│ }                                                   │
└──────────────────────────────────────────────────────┘
```

### 4️⃣ Agent Rating System Flow

```
┌──────────────────────────────────────────────────────┐
│ BUYER RATES AN AGENT                                │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ POST /api/v1/ratings/<profile_id>/                  │
│ {                                                    │
│   "rating": 5,                                      │
│   "comment": "Excellent service!"                   │
│ }                                                    │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ CreateAgentReviewAPIView Validation                 │
│                                                      │
│ ✓ Check 1: Agent exists & is_agent=True             │
│   → 404 if agent profile not found                   │
│                                                      │
│ ✓ Check 2: Self-rating prevention                   │
│   if rater.email == agent.user.email:               │
│     → 403: "You can't rate yourself"                │
│                                                      │
│ ✓ Check 3: Duplicate rating prevention              │
│   if Rating.objects.filter(                         │
│       rater=request.user,                           │
│       agent=agent_profile                           │
│     ).exists():                                      │
│     → 403: "You have already rated this agent"      │
│                                                      │
│ ✓ Check 4: Valid rating (1-5)                       │
│   if rating == 0:                                   │
│     → 400: "Please select a rating"                 │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Create Rating Record                                │
│ Rating.objects.create(                              │
│   rater=request.user,                               │
│   agent=agent_profile,                              │
│   rating=5,                                         │
│   comment="Excellent service!"                      │
│ )                                                    │
│                                                      │
│ Database:                                           │
│ ┌────────────────────────────────────────────────┐ │
│ │ rater_id | agent_id | rating | comment        │ │
│ │ UNIQUE(rater_id, agent_id)                     │ │
│ └────────────────────────────────────────────────┘ │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Update Agent Profile Stats                          │
│ (Aggregated from all ratings)                       │
│                                                      │
│ agent_profile.num_reviews = count(all_ratings)      │
│ agent_profile.avg_rating = avg(all_ratings)         │
│ agent_profile.top_agent = (avg_rating >= 4.5)?      │
│                                                      │
│ Profile Fields:                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ num_reviews | avg_rating | top_agent (bool)   │ │
│ └────────────────────────────────────────────────┘ │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Return Response (201 Created)                       │
│ {                                                    │
│   "details": "Review added successfully"            │
│ }                                                    │
└──────────────────────────────────────────────────────┘

GET /api/v1/profiles/agents/
→ All agents with is_agent=True

GET /api/v1/profiles/top-agents/
→ Filtered: top_agent=True (avg_rating >= 4.5)
→ Ordered by: num_reviews DESC, avg_rating DESC
```

### 5️⃣ Email Notification (Async) Flow

```
┌──────────────────────────────────────────────────────┐
│ USER SUBMITS CONTACT FORM (ENQUIRY)                 │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ POST /api/v1/enquiries/                             │
│ {                                                    │
│   "name": "John Buyer",                             │
│   "email": "buyer@example.com",                     │
│   "phone_number": "+91-98765-43210",                │
│   "subject": "Interested in oceanview property",    │
│   "message": "Can we schedule a viewing?"           │
│ }                                                    │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ SendEnquiryAPIView.post()                           │
│                                                      │
│ Step 1: Extract Request Data                        │
│ subject, name, email, message, phone_number         │
│                                                      │
│ Step 2: Queue Async Email Task                      │
│ send_mail(                                          │
│   subject = "Interested in oceanview property",    │
│   message = "Can we schedule a viewing?",          │
│   from_email = "buyer@example.com",                │
│   recipient_list = [DEFAULT_FROM_EMAIL],           │
│   fail_silently = True                             │
│ ) ← Queued to Celery (not executed yet)            │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Save Enquiry Record to Database                     │
│ Enquiry(                                            │
│   name="John Buyer",                                │
│   email="buyer@example.com",                        │
│   subject="Interested in oceanview property",       │
│   message="Can we schedule a viewing?",             │
│   phone_number="+91-98765-43210"                    │
│ ).save()                                            │
│                                                      │
│ Database Table:                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ id | name | email | phone | subject | message │ │
│ │ created_at | updated_at                        │ │
│ └────────────────────────────────────────────────┘ │
└──────────┬───────────────────────────────────────────┘
           │
           ▼ HTTP Response (Immediate)
┌──────────────────────────────────────────────────────┐
│ Client Response (Success)                           │
│ {                                                    │
│   "success": "Your Enquiry was successfully         │
│              submitted"                             │
│ }                                                    │
│ Status: 200 OK                                      │
└──────────────────────────────────────────────────────┘

┌─────────────────────────────────┐
│    BACKGROUND PROCESSING        │
│         (Async)                 │
└──────────────┬───────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Celery Task Queue (Redis)   │
    │ Task: send_enquiry_email    │
    │ Status: PENDING             │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Celery Worker Process       │
    │ (Listening to Redis)        │
    │ Picks up task               │
    │ Status: STARTED             │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Email Backend (SMTP)        │
    │ Email Provider: Gmail/SendGrid
    │ To: DEFAULT_FROM_EMAIL      │
    │ Subject: Interested in...   │
    │ Body: Can we schedule...    │
    │ From: buyer@example.com     │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Task Completed              │
    │ Status: SUCCESS             │
    └─────────────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Flower Dashboard            │
    │ View task execution history │
    │ (http://localhost:5557)     │
    └─────────────────────────────┘
```

### 6️⃣ Image Upload Flow

```
┌──────────────────────────────────────────────────────┐
│ AGENT UPLOADS PROPERTY IMAGES                        │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ POST /api/v1/properties/upload/                     │
│ Content-Type: multipart/form-data                   │
│                                                      │
│ FormData:                                           │
│ • property_id: "uuid-123"                           │
│ • cover_photo: [FILE]                               │
│ • photo1: [FILE]                                    │
│ • photo2: [FILE]                                    │
│ • photo3: [FILE]                                    │
│ • photo4: [FILE]                                    │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ upload_property_image(request)                      │
│                                                      │
│ Step 1: Extract property_id from request            │
│ property_obj = Property.objects.get(id=property_id) │
│                                                      │
│ Step 2: Get file uploads from request.FILES         │
│ cover_photo = request.FILES.get("cover_photo")      │
│ photo1 = request.FILES.get("photo1")                │
│ ... (repeat for photo2, photo3, photo4)             │
│                                                      │
│ Step 3: Validate files (Pillow)                     │
│ • Check file type (JPEG, PNG)                       │
│ • Check file size (max)                             │
│ • Check image dimensions (if required)              │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Save Files to Disk                                  │
│ /app/mediafiles/properties/                         │
│   ├── cover_photos/                                 │
│   │   └── uuid-123_cover.jpg                        │
│   ├── photo1s/                                      │
│   │   └── uuid-123_photo1.jpg                       │
│   ├── photo2s/                                      │
│   │   └── uuid-123_photo2.jpg                       │
│   ├── photo3s/                                      │
│   │   └── uuid-123_photo3.jpg                       │
│   └── photo4s/                                      │
│       └── uuid-123_photo4.jpg                       │
│                                                      │
│ Update Property Model                               │
│ property_obj.cover_photo = cover_photo              │
│ property_obj.photo1 = photo1                        │
│ ... (repeat for photo2, photo3, photo4)             │
│ property_obj.save()                                 │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Return Success Response                             │
│ {                                                    │
│   "success": "Images uploaded successfully"         │
│ }                                                    │
│ Status: 200 OK                                      │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Nginx Serves Images via /mediafiles/                │
│ GET /mediafiles/cover_photos/uuid-123_cover.jpg     │
│ → Returns image file with proper MIME type          │
│ → Client receives image URL in GET requests         │
└──────────────────────────────────────────────────────┘
```

---

## 💼 Business Logic & Workflows

### Key Business Concepts

#### 1. **User Roles**
```python
# Profile Model Fields
is_buyer: bool      # Can search properties, submit enquiries, rate agents
is_seller: bool     # Can sell properties (same as agent initially)
is_agent: bool      # Can list properties, receive ratings, get badge
top_agent: bool     # Computed: avg_rating >= 4.5 AND num_reviews >= 3

# Access Control:
- Create Property → requires is_agent=True
- Rate Agent → requires is_authenticated, agent_profile.is_agent=True
- Submit Enquiry → AllowAny (public endpoint)
- Search Properties → AllowAny (public endpoint)
```

#### 2. **Computed Fields**
```python
# Property Model
final_property_price = price + tax
# Example: price=5000000, tax=750000
# final_property_price = 5750000 (display to users)
```

#### 3. **Signal-Based Auto-Creation**
```python
# signals.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            gender="Other",
            country="KE"
        )
# When User created → Profile auto-created
# No manual user.profile.create() needed
```

#### 4. **View Tracking with IP Deduplication**
```python
# PropertyDetailAPIView.get()
x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
ip = x_forwarded_for.split(",")[0] if x_forwarded_for else REMOTE_ADDR

# Check if this IP already viewed this property
if not PropertyViews.objects.filter(property=property_obj, ip=ip).exists():
    PropertyViews.objects.create(property=property_obj, ip=ip)
    property_obj.views += 1  # Increment counter
    property_obj.save()

# Result:
# • Same IP on same property → view count increases by 1 (only)
# • Different IP on same property → view count increases by 1
# • Same IP on different property → separate view count
```

#### 5. **Async Email Processing**
```python
# settings/development.py
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
CELERY_BROKER_URL = "redis://redis:6379"

# Enquiry Submission Flow:
1. User submits form → HTTP request
2. API saves record to DB (fast)
3. API queues email task to Celery (non-blocking)
4. HTTP response returns immediately (user doesn't wait)
5. Celery worker picks up task from Redis queue
6. Worker sends email via SMTP (slow operation)
7. Worker marks task as complete in Redis

# Benefits:
- User doesn't wait for email delivery
- Email failures don't break user experience
- Can retry failed emails automatically
- Flower dashboard monitors task execution
```

#### 6. **Resource Ownership Validation**
```python
# Used in: Update, Delete endpoints
user = request.user
if property_obj.user != user:
    return Response(
        {"error": "You cannot update a property that doesn't belong to you"},
        status=status.HTTP_403_FORBIDDEN
    )
# Only property creator can modify/delete
# Acts as row-level security check
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.14+ (with venv)
- PostgreSQL 16+
- Redis 6+
- Git

### Local Development Setup

#### 1. Clone Repository
```bash
cd ~/Projects/Real\ Estate\ main
git clone <repository-url>
cd django-real-estate
```

#### 2. Create Virtual Environment
```bash
python3.14 -m venv .venv-py314

# macOS/Linux
source .venv-py314/bin/activate

# Windows
.venv-py314\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
```bash
# Copy example env
cp .env.example .env

# Edit .env with your config:
SECRET_KEY=<50-char-random-string>
DEBUG=False
ALLOWED_HOSTS="localhost 127.0.0.1"

# Database
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=real_estate_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=<password>
PG_HOST=localhost
PG_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<app-password>
EMAIL_PORT=587

# Celery
CELERY_BROKER=redis://localhost:6379/0
CELERY_BACKEND=redis://localhost:6379/0
```

#### 5. Database Setup
```bash
# Create PostgreSQL database
createdb real_estate_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

#### 6. Start Services

**Terminal 1 - Django Dev Server:**
```bash
python manage.py runserver
# Accessible at: http://localhost:8000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A real_estate worker -l info
```

**Terminal 3 - Celery Flower (Monitoring):**
```bash
celery -A real_estate flower
# Accessible at: http://localhost:5555
```

### Docker Compose Setup (Production-like)

```bash
# Build all services
docker-compose up --build -d

# Services available:
# • API: http://localhost:8000
# • Nginx: http://localhost:80
# • Flower: http://localhost:5557
# • Client: http://localhost:3000
# • PostgreSQL: localhost:5432
# • Redis: localhost:6379

# Verify services
docker-compose ps

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

---

## 📁 Project Structure

```
django-real-estate/
│
├── real_estate/                          # Django project config
│   ├── settings/
│   │   ├── base.py                       # Shared settings (AUTH, REST_FRAMEWORK, LOGGING)
│   │   ├── development.py                # Dev overrides (DEBUG=True, EMAIL_BACKEND)
│   │   └── production.py                 # Prod hardening (HTTPS, caching)
│   ├── urls.py                           # Main URL routing
│   ├── wsgi.py                           # WSGI entry point
│   ├── asgi.py                           # ASGI entry point (async)
│   └── celery.py                         # Celery app config
│
├── apps/                                 # Business logic (6 Django apps)
│   ├── users/                            # User model & auth
│   │   ├── models.py                     # CustomUser (email-based)
│   │   ├── managers.py                   # CustomUserManager
│   │   ├── views.py                      # (empty, handled by djoser)
│   │   ├── serializers.py                # User serializers
│   │   └── migrations/
│   │
│   ├── profiles/                         # User profiles & ratings
│   │   ├── models.py                     # Profile, Rating models
│   │   ├── views.py                      # GetProfileAPIView, UpdateProfileAPIView, AgentListAPIView, TopAgentsListAPIView
│   │   ├── serializers.py                # ProfileSerializer, UpdateProfileSerializer
│   │   ├── signals.py                    # post_save Profile auto-creation
│   │   ├── exceptions.py                 # ProfileNotFound, NotYourProfile
│   │   ├── renderers.py                  # Custom JSON renderer
│   │   ├── urls.py                       # Profile URLs
│   │   └── migrations/
│   │
│   ├── properties/                       # Property listings
│   │   ├── models.py                     # Property, PropertyViews models
│   │   ├── views.py                      # 9 view classes + 4 function-based views
│   │   ├── serializers.py                # PropertySerializer, PropertyCreateSerializer
│   │   ├── pagination.py                 # PropertyPagination (10 items/page)
│   │   ├── filters.py                    # PropertyFilter (django-filter)
│   │   ├── exceptions.py                 # PropertyNotFound
│   │   ├── urls.py                       # Property URLs
│   │   └── migrations/
│   │
│   ├── ratings/                          # Agent reviews
│   │   ├── models.py                     # Rating model
│   │   ├── views.py                      # CreateAgentReviewAPIView
│   │   ├── serializers.py                # RatingSerializer
│   │   ├── urls.py                       # Rating URLs
│   │   └── migrations/
│   │
│   ├── enquiries/                        # Contact form
│   │   ├── models.py                     # Enquiry model
│   │   ├── views.py                      # SendEnquiryAPIView
│   │   ├── serializers.py                # EnquirySerializer
│   │   ├── tasks.py                      # Celery tasks (send_email)
│   │   ├── urls.py                       # Enquiry URLs
│   │   └── migrations/
│   │
│   └── common/                           # Shared utilities
│       ├── models.py                     # TimeStampedUUIDModel (base class)
│       ├── pagination.py                 # Custom pagination
│       └── exceptions.py                 # Custom exceptions
│
├── client/                               # React frontend
│   ├── src/
│   │   ├── components/                   # React components
│   │   ├── features/                     # Redux slices
│   │   ├── pages/                        # Page components
│   │   └── App.jsx                       # Root component
│   └── package.json
│
├── docker/                               # Container configs
│   └── local/
│       ├── django/                       # Django Dockerfile
│       │   ├── Dockerfile
│       │   ├── entrypoint
│       │   ├── start
│       │   └── celery/
│       │       ├── celerybeat.start
│       │       ├── celeryworker.start
│       │       └── flower.start
│       └── nginx/
│           ├── Dockerfile
│           └── default.conf
│
├── tests/                                # Test suite
│   ├── factories.py                      # Factory-boy factories
│   ├── conftest.py                       # Pytest fixtures
│   └── [app]/test_*.py                   # Test files
│
├── docker-compose.yml                    # 8-service orchestration
├── Dockerfile                            # 3-stage production build
├── Makefile                              # Build automation
├── requirements.txt                      # 51 packages (pinned versions)
├── pytest.ini                            # Pytest configuration
├── setup.cfg                             # Setup configuration
├── manage.py                             # Django management CLI
├── AGENTS.md                             # Technical reference (14 sections)
├── CLAUDE.md                             # Development guidelines
└── README.md                             # This file
```

---

## 🔌 API Endpoints Reference

### Base URL: `/api/v1/`

### Authentication
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/auth/users/` | AllowAny | Register new user |
| POST | `/auth/jwt/create/` | AllowAny | Login (get tokens) |
| POST | `/auth/jwt/refresh/` | AllowAny | Refresh access token |
| POST | `/auth/jwt/verify/` | AllowAny | Verify token validity |
| POST | `/auth/users/reset_password/` | AllowAny | Request password reset |

### Profiles
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/profile/` | IsAuthenticated | Get logged-in user's profile |
| PATCH | `/profile/update/<username>/` | IsAuthenticated | Update own profile |
| GET | `/profile/agents/` | IsAuthenticated | List all agents |
| GET | `/profile/top-agents/` | IsAuthenticated | List top agents |

### Properties
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/properties/all/` | AllowAny | List published properties (paginated) |
| POST | `/properties/create/` | IsAuthenticated | Create property listing |
| GET | `/properties/details/<slug>/` | AllowAny | Get property detail + track views |
| PUT | `/properties/update/<slug>/` | IsAuthenticated | Update property (owner only) |
| DELETE | `/properties/delete/<slug>/` | IsAuthenticated | Delete property (owner only) |
| POST | `/properties/search/` | AllowAny | Advanced search with filters |
| POST | `/properties/upload/` | IsAuthenticated | Upload property images |
| GET | `/properties/views/` | AllowAny | List property view tracking |

### Ratings
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/ratings/<profile_id>/` | IsAuthenticated | Rate agent (1-5 stars) |

### Enquiries
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/enquiries/` | AllowAny | Submit contact form (triggers async email) |

---

## 🗄️ Database Schema

### Core Tables (6 Models)

```sql
-- Users (Custom)
users_user:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── username (VARCHAR 255) [UNIQUE]
  ├── email (EmailField) [UNIQUE, LOGIN FIELD]
  ├── password (hashed)
  ├── first_name, last_name
  ├── is_staff, is_active, is_superuser
  └── date_joined (DateTime)

-- Profiles (OneToOne with User)
profiles_profile:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── user (OneToOne → users_user CASCADE)
  ├── phone_number (PhoneNumberField)
  ├── about_me, license (TextField, CharField)
  ├── profile_photo (ImageField)
  ├── gender, country, city (CharField, CountryField)
  ├── is_buyer, is_seller, is_agent, top_agent (Boolean)
  ├── num_reviews (Int)
  ├── avg_rating (Decimal 2.1)
  ├── created_at, updated_at (DateTime)
  └── [Signal] auto_created on User.post_save

-- Properties
properties_property:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── user (ForeignKey → users_user, related_name=agent_buyer)
  ├── title (CharField 250, auto-slugs)
  ├── slug (AutoSlugField UNIQUE)
  ├── ref_code (CharField 255 UNIQUE)
  ├── description (TextField)
  ├── country, city, postal_code, street_address
  ├── property_number (Integer)
  ├── price (Decimal 8,2)
  ├── tax (Decimal 6,2)
  ├── final_property_price [COMPUTED: price + tax]
  ├── plot_area (Decimal 8,2)
  ├── total_floors, bedrooms (Integer)
  ├── bathrooms (Decimal 4,2)
  ├── advert_type (CharField: For Sale, For Rent, Auction)
  ├── property_type (CharField: House, Apartment, Office, ...)
  ├── cover_photo, photo1-4 (ImageField)
  ├── published_status (Boolean)
  ├── views (Integer)
  ├── created_at, updated_at (DateTime)
  └── managers: objects, published (PropertyPublishedManager)

-- Property Views (View Tracking)
properties_propertyviews:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── property (ForeignKey → properties_property CASCADE)
  ├── ip (GenericIPAddressField)
  ├── created_at, updated_at
  └── UNIQUE(property_id, ip)

-- Ratings (Agent Reviews)
profiles_rating:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── rater (ForeignKey → users_user SET_NULL)
  ├── agent (ForeignKey → profiles_profile SET_NULL)
  ├── rating (Integer 1-5)
  ├── comment (TextField nullable)
  ├── created_at, updated_at
  └── UNIQUE(rater_id, agent_id)

-- Enquiries (Contact Form)
enquiries_enquiry:
  ├── pkid (BigAutoField) [PK]
  ├── id (UUID) [UNIQUE]
  ├── name, subject (CharField)
  ├── phone_number (PhoneNumberField)
  ├── email (EmailField)
  ├── message (TextField)
  ├── created_at, updated_at
  └── [Signal] async email task queued on save
```

---

## 💻 Development Guidelines

### Code Standards
- **PEP 8 Compliance**: All files pass flake8 (max line: 100 chars)
- **Type Hints**: Return type annotations on all methods (`-> QuerySet`, `-> Response`)
- **Docstrings**: Module, class, function docstrings using Google style
- **Testing**: pytest-django + factory-boy (target: >80% coverage)

### Common Development Tasks

#### Add New Property Filter
```python
# apps/properties/filters.py
class PropertyFilter(django_filters.FilterSet):
    new_field = django_filters.CharFilter(
        field_name="new_field",
        lookup_expr="iexact"
    )
    
    class Meta:
        model = Property
        fields = ["advert_type", "property_type", "new_field"]
```

#### Add New Async Task
```python
# apps/enquiries/tasks.py
@shared_task
def send_custom_email(email, subject, message):
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [email])

# Usage in view:
send_custom_email.delay(email, subject, message)
```

#### Create New Serializer
```python
# apps/[app]/serializers.py
class NewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = YourModel
        fields = ["id", "user", "field1", "field2"]
    
    def get_user(self, obj):
        return obj.user.username
```

### Testing with Pytest
```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/properties/

# Run with coverage
pytest --cov=apps --cov-report=html

# View coverage
open htmlcov/index.html
```

### Debugging
```bash
# Django shell
python manage.py shell

# Check migrations status
python manage.py showmigrations

# Create migration
python manage.py makemigrations apps.your_app

# Run migrations
python manage.py migrate

# Flush database (dev only)
python manage.py flush --noinput
```

---

## 🔐 Security Checklist

- ✅ JWT tokens (not session-based)
- ✅ Password hashing (PBKDF2 by default)
- ✅ HTTPS in production (Nginx + SSL)
- ✅ CORS whitelisted (CSRF_TRUSTED_ORIGINS)
- ✅ Resource ownership validation (row-level security)
- ✅ Environment variables (no hardcoded secrets)
- ✅ SQL injection mitigated (ORM usage)
- ✅ CSRF protection enabled
- ✅ Authenticated endpoints require auth
- ✅ Rate limiting (TBD: use django-ratelimit or DRF throttling)

---

## 📝 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `psycopg2` connection error | PostgreSQL not running | `brew start postgresql` |
| Celery tasks not executing | Redis not running | `brew start redis` |
| 401 Unauthorized | Missing JWT token | Check `Authorization: Bearer <token>` header |
| 403 Forbidden (property) | Not property owner | Ensure `property.user == request.user` |
| 404 Profile not found | User profile not auto-created | Check signal in `profiles/signals.py` |
| Email not sending | Celery worker not running | Start Celery worker in separate terminal |
| Migrations conflict | Multiple migration files | Use `python manage.py showmigrations` |

---

## 📚 Documentation References

- **AGENTS.md**: 14-section technical reference (models, views, endpoints, patterns)
- **CLAUDE.md**: Quick reference guide
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Celery Docs**: https://docs.celeryproject.io/

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow PEP 8 (run `flake8 apps/`)
3. Add tests for new features
4. Ensure `python manage.py check` passes
5. Submit PR with clear description

---

## 📞 Support

For issues, questions, or feature requests, refer to [AGENTS.md](AGENTS.md) Section 14 (AI Collaboration Guide) or contact the development team.

---

**Version**: 2.0 | **Last Updated**: April 4, 2026 | **Status**: Production-Ready ✅
