# Dataclass Patterns: Semantic Field Documentation

## Overview

Dataclasses and structured data types require two levels of documentation: **class-level** (semantic role of the entire structure) and **field-level** (semantic meaning of each attribute).

This reference covers how to document **semantic intent** of fields without prescribing type choices, validation strategies, or serialization mechanics. Those belong to other skills.

## Class-Level Docstring

### Purpose

Document the **semantic role** of the dataclass in your domain. What problem does this data structure solve? What boundary does it represent?

### Template

```python
@dataclass
class YourStructure:
    """One-liner describing the structure's role.

    Extended description of semantic purpose, invariants, or domain context.
    Include any cross-field constraints that matter to callers.
    """
```

### Example: User in Authentication Context

```python
@dataclass
class User:
    """An authenticated user identity.

    Represents a user that has been successfully authenticated and identified
    in the system. All fields are populated from the authentication token or
    session store.
    """
```

### Example: Payment Order in Commerce Context

```python
@dataclass
class PaymentOrder:
    """A pending or completed payment transaction.

    Captures the financial obligation between customer and merchant.
    Invariant: total_amount must equal sum of line items. Immutable after creation.
    """
```

### What to Document

- ✅ **Semantic role**: What does this structure represent in your domain?
- ✅ **Boundary context**: When is this structure used? (e.g., "after authentication", "in checkout flow")
- ✅ **Invariants**: Cross-field constraints that matter to callers (e.g., "status must be one of...")
- ✅ **Mutability**: Is the structure mutable? When should it be immutable?

### What NOT to Document

- ❌ **Type choices**: Don't explain why fields use `str` vs `int` (that's `python-type-hints-strict`)
- ❌ **Validation mechanisms**: Don't explain `@field_validator` or validation rules (out of scope)
- ❌ **Serialization**: Don't explain JSON mappings or custom encoders (framework-specific)
- ❌ **Database schema**: Don't explain ORM mappings or column names (persistence-specific)

---

## Field-Level Docstrings

### Purpose

Each field should have a **one-liner docstring** capturing its semantic meaning in the domain. This is optional for trivial fields but recommended for any field whose purpose is not immediately obvious from its name.

### Template

```python
@dataclass
class Example:
    field_name: Type
    """Semantic meaning of this field in the domain."""
```

### Example: User Dataclass with Field Docs

```python
@dataclass
class User:
    """An authenticated user identity."""

    id: str
    """Unique user identifier. Primary key; immutable."""

    email: str
    """User's email address. Serves as secondary identifier; must be unique."""

    display_name: str
    """User's preferred display name (may differ from legal name)."""

    roles: list[str]
    """List of assigned role names (e.g., 'admin', 'viewer'). Empty if no roles."""

    last_login_at: datetime | None
    """Timestamp of the user's last successful login. None if never logged in."""
```

### Example: Payment Order with Field Docs

```python
@dataclass
class PaymentOrder:
    """A pending or completed payment transaction."""

    id: str
    """Unique transaction identifier assigned at creation."""

    customer_id: str
    """Foreign key linking to the customer who placed this order."""

    total_amount_cents: int
    """Order total in cents (not dollars). Positive integer. Immutable."""

    status: str
    """Current order status: 'pending', 'processing', 'completed', 'failed', 'refunded'."""

    items: list[OrderItem]
    """List of line items in this order. Must not be empty."""

    created_at: datetime
    """Timestamp when the order was created. Immutable."""

    notes: str | None
    """Optional customer notes or special instructions for this order."""
```

### Field Docstring Guidelines

| Aspect | Guidance |
|--------|----------|
| **Length** | One sentence; keep it short |
| **Tense** | Present tense (e.g., "User's email" not "Will store the user's email") |
| **Semantic focus** | What does this field mean in the domain? (not how it's stored/validated) |
| **Optional/Required** | Mention if field may be None or empty (e.g., "Optional; None if never set") |
| **Constraints** | Domain constraints visible to callers (e.g., "Must be positive", "One of: A, B, C") |
| **Relationships** | Foreign keys or references (e.g., "Foreign key to Customer") |

---

## When to Include Field Docs

### ✅ Always Document

- Fields with **obvious names but caller-visible semantics or conventions**: `created_at` (which event/time source?), `is_active` (what qualifies as active?), `batch_size` (items per batch for which operation?)
- Fields with **domain semantics**: `user_tier` (why does this matter?), `risk_score` (what does this measure?)
- Fields with **constraints**: `amount_cents` (why cents, not dollars?), `status` (what values are valid?)
- **Foreign keys or relationships**: `customer_id` (what does this link to?)
- **Optional fields**: `notes`, `last_login_at` (when is this None/empty?)

### ✅ May Skip

- Trivial fields where name alone conveys everything: `id` (if it's obvious)
- Simple container types where semantics are obvious: `items` in an `ItemList` (though a brief doc is still helpful)

### ❌ Never Document Here

- Type information (already in annotation): Don't say "str: User's name as a string" (say "User's preferred display name")
- Implementation details: Don't say "Stored in PostgreSQL users table" (that's persistence concern)
- Validation rules: Don't say "Validated by email_regex pattern" (that's `python-model-selection`)

---

## Examples: Contract vs Validation Boundary

### ❌ Anti-Pattern: Validation Details in Field Doc

```python
@dataclass
class CreateUserRequest:
    """Request to create a new user."""

    email: str
    """Email address; must be validated with the email_validator library and
    checked against existing users using the uniqueness_check() function."""
```

**Why this is wrong**:
- Documents implementation details (which library, which function)
- Mixes domain semantics with validation mechanics
- If validation strategy changes, docstring becomes stale

**Better version** (contract-focused):

```python
@dataclass
class CreateUserRequest:
    """Request to create a new user."""

    email: str
    """Email address for the new user. Must be unique across all existing users."""
```

---

### ✅ Correct: Domain Constraint Without Implementation

```python
@dataclass
class PaymentRequest:
    """Request to process a payment."""

    amount_cents: int
    """Payment amount in cents. Must be a positive integer."""

    currency: str
    """ISO 4217 currency code (e.g., 'USD', 'EUR'). Must be supported by processor."""

    customer_id: str
    """ID of the customer making the payment. Must be an existing customer."""
```

**Why this is correct**:
- **States the contract**: what the field means and what callers must ensure
- **Domain constraint only**: "must be positive", "must be existing", not "validated by validator X"
- **Portable**: Constraint is discoverable from domain context, not implementation

---

## Special Patterns

### Optional Fields

```python
@dataclass
class UserProfile:
    """A user's profile information."""

    bio: str | None
    """Optional user biography. Empty or None if not provided."""

    avatar_url: str | None
    """Optional URL to user's avatar image. None if no avatar has been uploaded."""

    preferred_language: str
    """User's preferred language code (e.g., 'en-US'). Defaults to 'en' if not set."""
```

### Enum-Like Fields

```python
@dataclass
class Order:
    """A customer order."""

    status: str
    """Order status. One of: 'pending', 'processing', 'completed', 'cancelled', 'refunded'."""

    priority: int
    """Order priority level. 1 (high) to 5 (low). Higher numbers = lower priority."""
```

### Composite Fields

```python
@dataclass
class LineItem:
    """A single line in an order."""

    product_id: str
    """ID of the product being ordered."""

    quantity: int
    """Number of units ordered. Must be positive."""

    unit_price_cents: int
    """Price per unit in cents. Captured at order time (may differ from current catalog price)."""

    total_price_cents: int
    """Total for this line (quantity × unit_price_cents). Immutable; computed at creation."""
```

### Nested Dataclasses

```python
@dataclass
class Address:
    """A postal address."""

    street: str
    """Street address line."""

    city: str
    """City or locality name."""

@dataclass
class Customer:
    """A registered customer."""

    id: str
    """Unique customer identifier."""

    billing_address: Address
    """Primary billing address for this customer. Required for payment processing."""

    shipping_addresses: list[Address]
    """List of shipping addresses on file. May be empty (use billing address if needed)."""
```

---

## Relationship Fields: Foreign Keys and References

### One-to-One Relationship

```python
@dataclass
class User:
    """An authenticated user."""

    id: str
    """User's unique identifier."""

    profile_id: str
    """Foreign key to the user's profile. One profile per user; must exist."""
```

### One-to-Many Relationship

```python
@dataclass
class Order:
    """A customer order containing one or more items."""

    id: str
    """Order's unique identifier."""

    customer_id: str
    """Foreign key to the Customer who placed this order."""

    line_items: list[LineItem]
    """Items in this order. Must contain at least one item."""
```

### Many-to-Many Relationship (via ID list)

```python
@dataclass
class Project:
    """A project with team members."""

    id: str
    """Project's unique identifier."""

    team_member_ids: list[str]
    """IDs of team members assigned to this project. May be empty before launch."""
```

---

## Class Invariants

When a dataclass has **cross-field constraints** that matter to callers, document them in the class docstring.

```python
@dataclass
class DateRange:
    """A range of dates with validation invariants."""

    start_date: date
    """Start of the date range."""

    end_date: date
    """End of the date range."""

    # Class-level constraint documented in class docstring:
    # Invariant: end_date must be >= start_date. This is enforced at construction.
```

Implement in docstring:

```python
@dataclass
class DateRange:
    """A contiguous range of calendar dates.

    Invariant: end_date >= start_date. This constraint is enforced at construction
    and may be assumed by all callers.
    """

    start_date: date
    """Start of the date range (inclusive)."""

    end_date: date
    """End of the date range (inclusive)."""
```

---

## Mutability and Immutability

### Immutable Dataclass

```python
@dataclass(frozen=True)
class UserIdentity:
    """An immutable user identity snapshot.

    All fields are immutable after construction. Safe to cache or compare directly.
    """

    id: str
    """User's unique identifier. Immutable."""

    email: str
    """User's email at identity capture time. Immutable."""
```

### Mutable Dataclass

```python
@dataclass
class UserProfile:
    """A mutable user profile.

    Fields may be updated after construction (e.g., display name, preferences).
    """

    id: str
    """User's unique identifier. Immutable."""

    display_name: str
    """User's current display name. Mutable; callers may modify."""
```

---

## Anti-Patterns

### ❌ Over-Documenting Trivial Fields

```python
@dataclass
class User:
    """A user."""

    id: str
    """The unique identifier for the user. This is an immutable field that never changes."""

    name: str
    """The name of the user. This is a string that represents the user's name."""
```

**Problem**: Noise; name and type are obvious. Field docs should add value, not repeat.

**Better**:
```python
@dataclass
class User:
    """A user."""

    id: str
    """Unique user identifier."""

    name: str
    """User's preferred display name."""
```

---

### ❌ Mixing Validation and Semantics

```python
@dataclass
class BankAccount:
    """A bank account."""

    balance_cents: int
    """Current balance in cents. Must be validated to ensure it's non-negative
    and doesn't exceed the maximum account balance of 999,999,999 cents."""
```

**Problem**: Mixes domain semantics (what the field is) with validation (how it's checked).

**Better**:
```python
@dataclass
class BankAccount:
    """A bank account."""

    balance_cents: int
    """Current account balance in cents. Non-negative."""
```

---

## Summary

**Class-level docstring**:
- **Semantic role**: What does this structure represent?
- **Boundary context**: When/how is it used?
- **Invariants**: Cross-field constraints?

**Field-level docstring**:
- **Semantic meaning**: What does this field represent in the domain?
- **Domain constraints**: What values are valid? (not HOW they're validated)
- **Relationships**: Foreign keys, references?
- **Optional status**: When is this field None or empty?

**Keep field docs concise, domain-focused, and decoupled from implementation/validation details.**
