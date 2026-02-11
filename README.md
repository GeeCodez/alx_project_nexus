# **ALX PROJECT NEXUS - ECOMMERCE BACKEND**

## **Project Overview**

This project is a production-style **E-commerce Backend API** built using **Django Rest Framework**, designed to simulate real-world industry backend architecture.

The system supports:

- Custom user authentication (JWT)
- Product catalog management
- Order processing
- Payment processing via Paystack (Mobile Money)
- Secure webhook handling
- Scalable database design
- Performance optimization using query optimization techniques
- Redis Caching
- Background Jobs using Celery
- Email Notifications

This project was built as part of **ALX PRODEV BACKEND COURSE**, demonstrating readiness for professional backend development roles.

---

## **Core Features**

### **Authentication & User Management**

- Custom User Model (Username / Email / Phone login support)
- JWT Authentication (Access + Refresh Tokens)
- Secure Password Validation
- Login Rate Limiting (Throttle Protection)

### **Product Management**

- Category-based product organization
- Search, filter, and ordering support
- Pagination support
- Active product visibility control

### **Order Management**

- Multi-item order creation
- Transaction-safe order processing
- Bulk order item creation for performance
- Order cancellation logic with status validation

### **Payment Processing**

- Paystack Payment Integration
- Mobile Money Support
- Secure Payment Initialization
- Webhook Payment Verification
- Signature Validation for Security (HMAC SHA512)
- Atomic Payment + Order Status Updates

---

## **System Architecture**

- Client → DRF API → Services Layer → Database
- Services Layer → Paystack API

---

## **Tech Stack**

### **Backend**

- Django
- Django Rest Framework
- SimpleJWT
- PostgreSQL

### **Integrations**

- Paystack Payment Gateway
- Mobile Money Payments

### **Development Tools**

- DRF YASG (Swagger Documentation)
- Django Filters
- Python Dotenv
- Ngrok (Webhook Testing)

---

## **Database Design Principles**

- Normalized relational schema
- Indexed frequently queried fields
- Transaction-safe operations
- Foreign key protection on critical data
- Optimized query loading using *select_related* and *prefetch_related*

---

## **Performance Optimizations**

- Bulk create for order items
- Query optimization to avoid N+1 queries
- Indexed fields for filtering and searching
- Throttling for abuse prevention

---

## **Security Best Practices**

- JWT Authentication
- Secure Webhook Signature Verification (HMAC SHA512)
- Environment Variable Secret Management
- Login Rate Limiting
- CSRF exemption only for verified webhook endpoints

---

## **Key API Modules**

- **Accounts** – Authentication & User Management
- **Products** – Product Catalog
- **Orders** – Order Processing
- **Payments** – Payment Gateway Integration

---

## **Testing**

- API Test Tools
- Webhook Simulation using Ngrok
- Manual Endpoint Validation

---

## **Deployment Readiness**

- PostgreSQL Production Database configuration
- Environment Variable Secret Management
- Static File Collection

---

## **Future Improvements**

- Refund Handling Automation
