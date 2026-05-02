# B2B Mobile App Technical Blueprint

## 1. Product Direction

### Working product
A mobile-first B2B commerce platform for imitation jewellery buyers.

### Launch principle
- browsing is open to everyone
- login is required for cart, order placement, order history, and saved items
- the first release supports imitation jewellery only
- the system is designed so kitchenware and hardware can be added later without re-architecting

### Business model for v1
Manufacturer-led wholesale platform backed by your family's Rajkot factory.

This means the first version is not a multi-seller marketplace. It is a single-business B2B commerce app with room to evolve into a multi-supplier system later.

That is the simplest and safest way to launch.

## 2. Recommended Stack

### Core stack
- mobile app: React Native with Expo and TypeScript
- admin panel: React with Vite and TypeScript
- backend API: FastAPI
- ORM: SQLAlchemy 2.x or SQLModel
- migrations: Alembic
- database: PostgreSQL via Supabase
- object storage: Supabase Storage
- notifications: Expo Notifications
- background jobs: FastAPI background tasks initially
- hosting: Render, Railway, or Fly.io for FastAPI

### Why this stack fits
- low upfront cost
- fast MVP delivery
- easy for you to own as a Python developer
- managed Postgres avoids early DevOps overhead
- mobile stack is flexible and well supported
- admin panel stays cheap and easy to iterate

## 3. Architecture

```text
Mobile App (Expo)
    |
    | HTTPS
    v
FastAPI Backend
    |
    | SQLAlchemy / SQLModel
    v
Supabase Postgres

FastAPI Backend --> Supabase Storage
FastAPI Backend --> Expo Push Service
Admin Panel -----> FastAPI Backend
```

### Ownership boundaries
- FastAPI owns business rules, auth checks, inventory logic, order lifecycle, and admin permissions
- Postgres is the source of truth
- Supabase is used as managed infrastructure, not as the place for core business logic
- the app and admin panel never bypass the API for business-critical write operations

## 4. User Roles

### Guest
- browse categories
- browse products
- search and filter
- view product details

### Buyer
- login and manage profile
- add items to cart
- place bulk orders
- view order history
- receive order updates
- save favorites

### Admin
- manage categories
- manage products
- manage product images and variants
- manage inventory
- track and update orders
- view customers
- receive new order notifications

## 5. MVP Scope

### Buyer app screens
- splash / onboarding
- home
- category list
- product listing
- product details
- search
- cart
- checkout
- login / signup
- profile
- my orders
- order details
- favorites
- notifications

### Admin panel screens
- login
- dashboard
- categories
- products
- add/edit product
- inventory
- orders
- order details
- customers
- notification center

## 6. Functional Requirements

### Catalog
- category-wise product management
- multiple images per product
- variants such as color, plating, size, set type
- SKU support
- MOQ support
- optional tiered pricing
- active/inactive product control

### Cart and ordering
- enforce MOQ before checkout
- prevent ordering inactive products
- allow quantity updates in cart
- create order with snapshot pricing
- support pending to confirmed to packed to shipped to delivered workflow

### Inventory
- maintain current stock per product or variant
- reserve inventory when order is confirmed
- deduct inventory on dispatch or confirmation based on business rule
- low-stock indicator in admin

### Notifications
- admin receives push notification when a new order is placed
- buyer receives push notification when order status changes

## 7. Data Model

### Core tables

#### users
- id
- full_name
- email
- phone
- password_hash or external_auth_id
- role (`buyer`, `admin`)
- is_active
- created_at

#### buyer_profiles
- user_id
- business_name
- gst_number
- city
- state
- address
- pincode

#### categories
- id
- name
- slug
- description
- image_url
- sort_order
- is_active

#### products
- id
- category_id
- name
- slug
- description
- sku
- base_price
- moq
- material
- plating
- weight_grams
- is_active
- created_at
- updated_at

#### product_variants
- id
- product_id
- variant_name
- variant_value
- sku
- price_override
- moq_override
- is_active

#### product_images
- id
- product_id
- variant_id nullable
- image_url
- alt_text
- sort_order

#### inventory
- id
- product_id
- variant_id nullable
- available_qty
- reserved_qty
- reorder_level
- updated_at

#### carts
- id
- user_id
- status
- created_at
- updated_at

#### cart_items
- id
- cart_id
- product_id
- variant_id nullable
- quantity

#### orders
- id
- order_number
- user_id
- status
- subtotal
- tax_amount
- shipping_amount
- total_amount
- payment_status
- notes
- shipping_address_snapshot
- created_at
- updated_at

#### order_items
- id
- order_id
- product_id
- variant_id nullable
- product_name_snapshot
- sku_snapshot
- unit_price_snapshot
- quantity
- line_total

#### device_tokens
- id
- user_id
- expo_push_token
- platform
- is_active
- created_at

#### notifications
- id
- user_id
- type
- title
- body
- payload_json
- is_read
- created_at

### Future-ready tables
- price_tiers
- business_verifications
- suppliers
- supplier_products
- payment_transactions
- returns

## 8. API Modules

### Public APIs
- `GET /health`
- `GET /categories`
- `GET /categories/{slug}/products`
- `GET /products`
- `GET /products/{slug}`

### Auth APIs
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

### Buyer APIs
- `GET /me`
- `PATCH /me`
- `GET /cart`
- `POST /cart/items`
- `PATCH /cart/items/{id}`
- `DELETE /cart/items/{id}`
- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`
- `POST /devices/register`
- `GET /notifications`

### Admin APIs
- `GET /admin/dashboard`
- `POST /admin/categories`
- `PATCH /admin/categories/{id}`
- `DELETE /admin/categories/{id}`
- `POST /admin/products`
- `PATCH /admin/products/{id}`
- `DELETE /admin/products/{id}`
- `POST /admin/products/{id}/images`
- `PATCH /admin/inventory/{id}`
- `GET /admin/orders`
- `GET /admin/orders/{id}`
- `PATCH /admin/orders/{id}/status`
- `GET /admin/customers`

## 9. Auth Strategy

### Recommended v1
- email + password login
- phone number stored on profile
- JWT access token + refresh token
- role-based authorization in FastAPI

### Why not OTP first
OTP adds SMS vendor cost and delivery complexity early.

For MVP, email/password is cheaper and easier. If your buyer base strongly prefers phone-first login, add OTP in phase 2.

## 10. Notification Strategy

### v1
- app registers Expo push token after login
- token is stored in `device_tokens`
- backend sends push notification through Expo Push Service

### Trigger events
- new order placed -> notify admins
- order status updated -> notify buyer
- low stock -> admin dashboard alert first, push optional later

## 11. Inventory Logic

### Recommended rule for v1
- cart does not reserve stock
- order creation validates available stock
- order confirmation moves quantity to reserved
- dispatch deducts from available and releases reserved

This keeps the flow practical while avoiding stock lock from abandoned carts.

## 12. Repo Strategy

### Recommended repository shape
Use one monorepo initially:

```text
/apps/mobile
/apps/admin
/services/api
/docs
```

### Why monorepo first
- simpler project setup
- shared docs and decisions in one place
- easier coordinated changes across app, admin, and backend
- lower overhead while team size is small

Split into multiple repos later only if the team or deployment process truly needs it.

## 13. GitHub vs GitLab

### Recommendation
Use GitHub unless you already have a strong reason to choose GitLab.

### Why GitHub is the better fit here
- better ecosystem for Expo, React Native, and FastAPI starters
- easier integration with CI, templates, and community actions
- simpler collaboration if you work with freelancers later
- broader community examples
- smoother fit if you later add issue tracking, discussions, or external contributors

### When GitLab would make sense
- you want self-hosting
- you already use GitLab CI heavily
- your team wants GitLab’s integrated DevOps workflow from day one

For your current stage, GitHub is the more practical choice.

## 14. CI/CD Recommendation

### v1 setup
- GitHub repository
- GitHub Actions for lint and test
- deploy FastAPI on push to `main`
- Expo EAS for mobile builds
- admin deployed on Vercel or Netlify

### Basic workflows
- backend lint + tests
- mobile typecheck + lint
- admin typecheck + lint

## 15. Delivery Roadmap

### Phase 0: foundation
- finalize feature scope
- create wireframes
- set up repo and environments
- define database schema

### Phase 1: backend and admin core
- auth
- categories
- products
- product images
- inventory
- order management

### Phase 2: buyer app MVP
- public catalog
- login
- cart
- checkout
- my orders

### Phase 3: push notifications and refinement
- admin new-order push
- buyer order-update push
- dashboard improvements
- analytics and low-stock views

### Phase 4: B2B hardening
- GST fields
- price tiers
- business verification
- manual approval for premium buyers

## 16. What You Can Build First

If you want the fastest execution path, start with this exact build order:

1. database schema
2. FastAPI auth and roles
3. category and product CRUD
4. inventory module
5. order creation and order status flow
6. admin panel
7. mobile buyer app
8. notifications

## 17. Suggested Immediate Next Tasks

- create the monorepo structure
- define the Postgres schema in SQLAlchemy or SQLModel
- write the backend PRD and endpoint contracts
- sketch the mobile screen flow
- set up GitHub repo and base CI

## 18. Final Recommendation

Build this as a single-brand B2B wholesale mobile app first, not as a general marketplace.

Use:
- Expo for mobile
- FastAPI for backend
- Supabase Postgres and Storage
- React admin panel
- GitHub monorepo

That gives you the best mix of speed, control, low cost, and future flexibility.
