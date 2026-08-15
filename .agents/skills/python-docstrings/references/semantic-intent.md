# Semantic Intent: From Explicit Signals to Contract-Only

## The Core Challenge

The hardest part of writing docstrings is **deciding whether to explain "why"** a callable exists. Some code has clear semantic intent visible in its context; other code is purely mechanical and should not speculate.

**Rule**: Derive intent only from **explicit code-adjacent signals**. If intent is not explicit, write a **contract-only docstring** instead and do not invent rationale.

## Explicit Signals

These signals make "why" discoverable:

1. **Symbol name** — Conveys primary intent via naming convention
   - Example: `authenticate_user` clearly indicates authentication as primary purpose
   - Example: `_normalize_email` as a private helper; intent is mechanical/local

2. **Module or class role** — Provides boundary context
   - Example: A function in `auth.py` has different "why" context than one in `utils.py`
   - Example: A method in `UserRepository` class signals data access as its role

3. **Parameter names and types** — Signal intent through naming
   - Example: `def verify_jwt(token, secret_key)` signals security verification
   - Example: `def process_items(items)` is purely mechanical; no "why" implied

4. **Return type and error types** — Declare what can go wrong
   - Exception types signal error contract; business types signal result handling
   - Example: Raising `JWTError` signals "this is about JWT validation"

5. **Surrounding public API** — Provides larger context
   - Example: If a class is titled "Primary authentication entry point", its methods inherit that boundary
   - Example: If module docstring explains "REST API handlers", its functions are scoped to that boundary

6. **Explicit constraints in code** — Guards, validators, preconditions
   - Example: `if not isinstance(email, str): raise ValueError(...)` signals contract enforcement
   - Example: `@dataclass` with type hints signals structured data semantics

## Derivation Method

### Step 1: Identify the Boundary

Look at the broadest context first: **module**, **class**, or **API boundary**.

- If module docstring says "Authentication for REST APIs", all functions inherit that boundary
- If class name is `UserRepository`, methods are scoped to data access
- If function is named `_internal_helper`, its scope is implementation-local

### Step 2: Check for Explicit "Why" Signals

Ask: **Can I discover the "why" from the code and nearby context alone?**

- ✅ Explicit from name + boundary: `authenticate_user` in an `auth.py` module → "why" is clear
- ✅ Explicit from parameter names: `verify_signature(public_key, signature)` → security purpose is clear
- ✅ Explicit from error types: Raising `PermissionError` → access control purpose is clear
- ❌ Not explicit from code: `process_data(data)` in a generic utilities module → no discoverable "why"

### Step 3: Write or Skip the Extended Description

**If Step 2 found explicit signals:**
- Write a brief extended description capturing the boundary and intent
- Example: "Authenticate a user using a JWT token. This is the primary authentication entry point for REST API requests."

**If Step 2 found NO explicit signals:**
- **Do NOT invent** a business rationale
- Write a **contract-only docstring**: focus on "what contract does this enforce?"
- Example: For `normalize_email(email)` — just document the input/output contract, not speculative "why"

## Examples: Intent Derivation

### Example 1: Explicit Intent from Boundary Context

```python
# Module docstring:
"""Authentication utilities for JWT-based API access."""

def authenticate_user(token: str, secret_key: str) -> User:
    """Authenticate a user using a JWT token.

    Verifies the JWT signature against the provided secret key and extracts the
    embedded user identity. This is the primary authentication entry point for
    REST API requests.

    Args:
        token: A JWT-formatted bearer token from the request Authorization header.
        secret_key: The HMAC secret key used to verify the token signature.

    Returns:
        User: A user object with id, email, and roles extracted from token claims.

    Raises:
        JWTError: If token signature is invalid or token is expired.
    """
```

**Why this is correct**:
- Module boundary ("Authentication utilities for JWT-based API access") provides explicit context
- Function name (`authenticate_user`) reinforces the intent
- Parameter names and types (`token`, `secret_key`) signal security verification
- Error types (`JWTError`) confirm authentication semantics
- **"Why" is derived from code-adjacent signals, not invented**

---

### Example 2: No Explicit Intent, So Contract-Only Docstring

```python
def normalize_email(email: str) -> str:
    """Return a lowercase, trimmed email address.

    Args:
        email: An email string, potentially with whitespace or mixed case.

    Returns:
        str: The email normalized to lowercase and without leading/trailing whitespace.
    """
```

**Why this is correct**:
- Function name `normalize_email` is mechanical; doesn't signal a "why"
- Parameters and return type are purely mechanical
- No module boundary or class role context (or generic context like `utils.py`)
- **Docstring does NOT invent "for matching user records" or "for database consistency"**
- **Docstring states the contract clearly**: input → output transformation

---

### Example 3: Private Method with Explicit Independent Contract

```python
class PaymentProcessor:
    def _translate_payment_error(self, api_error: APIError) -> PaymentError:
        """Translate an external payment API error to internal domain error.

        Maps vendor-specific error codes to domain-level PaymentError types.
        This translation ensures callers do not depend on third-party API contracts.

        Args:
            api_error: Error returned by the payment API.

        Returns:
            PaymentError: A domain error with translated error code and message.

        Raises:
            ValueError: If the API error code is unmapped or invalid.
        """
```

**Why this is correct**:
- Private method (prefix `_`), BUT it has explicit independent signals:
  - **State mutation context**: This is part of `PaymentProcessor` (domain boundary)
  - **Error translation**: Explicit signal that this has non-obvious contract
  - **Semantic return**: `PaymentError` is domain-typed, not a generic value
  - **Preconditions**: Error code mapping is a contract precondition
- These signals justify a full docstring, not just one-liner

---

### Example 4: Private Helper Without Independent Contract (One-Liner Only)

```python
class UserRepository:
    def _build_query_filter(self, role: str) -> dict:
        """Build a database query filter dict for the given role."""
        return {"role": role, "is_active": True}
```

**Why this is correct**:
- Private method (`_` prefix)
- No explicit independent contract signals:
  - ❌ Not a boundary translator (local implementation detail)
  - ❌ No semantic return (just a dict with obvious key/value pairing)
  - ❌ No error handling or preconditions (mechanical filtering)
  - ❌ Only called from one place or simple enough that name explains it
- **One-liner is sufficient**; full docstring would be noise

---

### Example 5: Dataclass with Field-Level Semantic Intent

```python
@dataclass
class PaymentOrder:
    """A payment order in the system."""

    id: str
    """Unique order identifier. Must be unique across all payment orders."""

    amount_cents: int
    """Order total in cents (not dollars). Must be positive. Required for billing."""

    customer_id: str
    """Foreign key to customer. Links this order to the customer who placed it."""

    status: str
    """Current order status: 'pending', 'processing', 'completed', or 'failed'."""
```

**Why this is correct**:
- Each field has **semantic intent visible from context**: dataclass name (`PaymentOrder`), field name, and type
- Docstring captures **domain meaning**: what each field represents in the business model
- Docstring does NOT say "validated by @field_validator" (implementation detail, out of scope)
- Docstring does NOT choose between `int` vs `float` or `str` vs `Enum` (that's `python-type-hints-strict` and `python-model-selection`)
- **Semantic role is explicit from the dataclass boundary**

---

## Anti-Patterns: Invented Intent

### ❌ Anti-Pattern 1: Business Rationale Not Discoverable from Code

```python
def calculate_discount(purchase_total: float) -> float:
    """Calculate a discount on the purchase to increase customer lifetime value.

    We offer discounts to boost loyalty and repeat purchases. This drives our
    retention metrics and improves profitability.
    """
```

**Why this is wrong**:
- The docstring invents a business strategy ("increase customer lifetime value") not visible in code
- Code does not show that this is a customer retention strategy
- If business priorities change, this docstring becomes incorrect and misleading
- **Caller only needs to know**: "Given a purchase total, return the discount amount"

**Better version (contract-only)**:
```python
def calculate_discount(purchase_total: float) -> float:
    """Return the discount amount for the given purchase total.

    Args:
        purchase_total: The order total in dollars.

    Returns:
        float: The discount amount in dollars. Always non-negative.
    """
```

---

### ❌ Anti-Pattern 2: Implementation Detail Presented as Intent

```python
def fetch_user_by_id(user_id: int) -> User:
    """Fetch a user by ID from the database.

    This function queries the PostgreSQL database users table using an indexed
    lookup on the user_id column. We use prepared statements to prevent SQL injection.
    """
```

**Why this is wrong**:
- Docstring explains **how** (PostgreSQL, indexed lookup, prepared statements)
- Docstring should explain **why** and **what contract** (what goes in, what comes out)
- Implementation details (query strategy, security technique) change; intent should not
- Caller does not need to know query internals

**Better version (contract-focused)**:
```python
def fetch_user_by_id(user_id: int) -> User:
    """Return the user with the given ID.

    Args:
        user_id: A positive integer user ID.

    Returns:
        User: The user object with full profile data.

    Raises:
        UserNotFound: If no user exists with the given ID.
    """
```

---

## When Intent Is Ambiguous

If you're unsure whether intent is explicit, ask:

1. **Can a new developer understand the "why" from the symbol name, type signature, error types, and module boundary alone?**
   - YES → Write extended description capturing that intent
   - NO → Write contract-only docstring

2. **Does the code depend on specific business context beyond the public API?**
   - YES → That context is implicit; write contract-only instead
   - NO → Intent is explicit from code-adjacent signals

3. **Would this docstring become incorrect if the business strategy changed?**
   - YES → You've invented intent; switch to contract-only
   - NO → Intent is properly tied to code semantics
