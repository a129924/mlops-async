# Examples: Detailed Scenarios

This file provides 5 positive and 3 negative representative scenarios with detailed explanations. These examples cover the key decision points and anti-patterns for writing clear, contract-first docstrings.

## Positive Scenarios

### Scenario A: Public Class with Semantic Intent Explicit from Boundary Context

**Situation**: A class represents a core domain entity. Its role is clear from class name and module context.

```python
# In auth_service.py module: "Service for managing user authentication"

@dataclass
class AuthToken:
    """A cryptographic token used to authenticate API requests.

    Each token is bound to a specific user and session. Tokens expire
    after a fixed duration and may be revoked. This is the primary credential
    type for stateless REST API authentication.

    Attributes:
        token_str: The opaque token string (do not inspect or parse).
        user_id: ID of the user this token authenticates.
        expires_at: Timestamp when this token becomes invalid.
        scopes: List of permission strings (e.g., 'read:users', 'write:orders').
    """

    token_str: str
    """The raw token string. Treated as opaque by callers."""

    user_id: str
    """ID of the authenticated user. Immutable."""

    expires_at: datetime
    """Expiration timestamp in UTC. Token is invalid after this time."""

    scopes: list[str]
    """List of granted permission strings (e.g., 'read:users', 'write:orders').
    Empty list if no explicit scopes granted."""
```

**Why this is correct**:
- **Class docstring** captures semantic role ("primary credential type for REST API") derived from explicit module boundary ("auth_service")
- **Field docstrings** each clarify domain meaning: token_str is "opaque" (caller shouldn't parse), user_id "immutable" (caller shouldn't modify), expires_at is UTC (temporal semantics)
- **Scope field** documents meaning without prescribing validation (doesn't say "must match allowed scope list")
- All intent is **discoverable from code-adjacent context** (module, class name, field names, types)

---

### Scenario B: Public Function Where Intent Is Not Explicit, So Contract-Only Docstring

**Situation**: A utility function with clear type signature but generic purpose. Intent is not discoverable from name alone in its module.

```python
# In utils.py (generic utilities module)

def slugify(text: str) -> str:
    """Return a URL-safe slug derived from the input text.

    Converts to lowercase, removes non-alphanumeric characters, and
    replaces spaces with hyphens.

    Args:
        text: Any string (whitespace, special characters, mixed case allowed).

    Returns:
        str: A lowercase slug suitable for URLs. Example: "hello-world".

    Example:
        >>> slugify("Hello, World!")
        'hello-world'
    """
```

**Why this is correct**:
- **No invented "why"**: Docstring doesn't say "for URL routing" or "for SEO" (not discoverable from code)
- **Pure contract**: Input is "any string", output is "URL-safe slug"
- **Generic and portable**: Example shows typical usage without project-specific context
- **No semantic intent section** because intent is not explicit from code-adjacent signals

---

### Scenario C: Private Helper with No Independent Contract (One-Liner Only)

**Situation**: A private method that is a local implementation detail with no independent caller-facing contract.

```python
class UserRepository:
    """Data access layer for User entities."""

    def _build_filter_dict(self, status: str) -> dict:
        """Build a query filter dict for users with the given status."""
        return {"status": status, "is_deleted": False}

    def find_active_users(self, status: str) -> list[User]:
        """Return all active users with the given status.

        Args:
            status: One of 'premium', 'standard', 'trial'.

        Returns:
            list[User]: All non-deleted users matching the status.
        """
        filter_dict = self._build_filter_dict(status)
        return self.db.query(filter_dict)
```

**Why this is correct**:
- **Private method** (`_build_filter_dict`) is a local implementation helper
- **One-liner is sufficient**: Method does one mechanical thing (build a dict), callable only from one place
- **No independent contract signals**: No error handling, no domain-typed return, no preconditions
- **Not documenting as full docstring** avoids noise and keeps code readable

---

### Scenario D: Private Helper with Independent Contract (State Mutation + Error Translation)

**Situation**: A private method that is reused from multiple call sites and translates domain errors. Its contract matters for internal correctness.

```python
class PaymentProcessor:
    """Orchestrates payment transactions with external API."""

    def _translate_vendor_error(self, vendor_code: str) -> PaymentError:
        """Translate a vendor error code to internal PaymentError.

        Maps third-party payment processor error codes to domain-level error types.
        This isolation ensures internal code does not depend on vendor API contracts.

        Args:
            vendor_code: Error code returned by payment processor API (e.g., 'CARD_DECLINED').

        Returns:
            PaymentError: A domain error with translated code and recoverable message.

        Raises:
            UnmappedVendorError: If the vendor code is not recognized (indicates
                vendor API contract change or incomplete error mapping).
        """
        # Implementation omitted
        pass

    def process_payment(self, card: Card, amount: int) -> Result[Payment, PaymentError]:
        """Process a payment for an order.

        Submits the card and amount to the external payment processor and
        translates any errors to domain types.

        Args:
            card: Card details for payment (PCI data is handled by processor).
            amount: Payment amount in cents (must be positive).

        Returns:
            Ok(Payment): On successful processing; includes transaction ID.
            Err(PaymentError): On payment failure; includes domain error code.
        """
        try:
            result = self.vendor_client.charge(card, amount)
            return Ok(Payment(transaction_id=result.id))
        except VendorError as e:
            error = self._translate_vendor_error(e.code)
            return Err(error)
```

**Why this is correct**:
- **Private method but with independent contract signals**:
  - **Error translation**: Changes error type (contract boundary)
  - **Preconditions matter**: Vendor code must be recognized (or raise UnmappedVendorError)
  - **Reused logic**: Called from multiple sites within the class
- **Full docstring justified**: Other methods in the class depend on this contract
- **Isolation semantics documented**: "ensures internal code does not depend on vendor API contracts" (explains the "why")
- **Error semantics clear**: Raises UnmappedVendorError on contract breach; returns domain PaymentError on success

---

### Scenario E: Dataclass with Field-Level Semantic Documentation and Contract-vs-Validation Boundary

**Situation**: A dataclass models domain entities. Fields have semantic meaning, but validation mechanics are out of scope.

```python
@dataclass
class CustomerOrder:
    """A purchase order from a customer.

    Represents a financial commitment between customer and seller.
    Invariant: total_amount_cents must equal sum of line items.
    Immutable after creation except for status updates.
    """

    id: str
    """Unique order identifier. Assigned at creation; immutable."""

    customer_id: str
    """Foreign key to the Customer placing this order. Immutable."""

    total_amount_cents: int
    """Total order amount in cents (not dollars). Must be positive and equal to
    sum of line items. Immutable."""

    status: str
    """Current order status. One of: 'pending', 'processing', 'completed',
    'cancelled', 'refunded'. Initially 'pending'; may transition to other states
    over the order lifecycle."""

    line_items: list[OrderItem]
    """Ordered items. Must contain at least one item. Immutable."""

    created_at: datetime
    """Timestamp when order was created. UTC timezone. Immutable."""

    notes: str | None
    """Optional customer notes or special instructions for this order.
    May be empty or None."""

@dataclass
class OrderItem:
    """A single line item in an order."""

    product_id: str
    """ID of the product being ordered. Immutable."""

    quantity: int
    """Number of units ordered. Must be positive. Immutable."""

    unit_price_cents: int
    """Price per unit in cents at order time. May differ from current catalog price
    (protects against retroactive price changes). Immutable."""

    total_price_cents: int
    """Total for this line (quantity × unit_price_cents). Immutable; computed at creation."""
```

**Why this is correct**:
- **Class docstring** captures domain semantics: "financial commitment", states invariant
- **Each field docstring** explains semantic meaning (foreign key, domain constraint, mutability)
- **Contract-only, not validation**: Field docs mention "must be positive" (domain constraint visible to callers) but NOT "validated by @field_validator" (implementation detail, out of scope)
- **Mutability** is documented (affects caller behavior): immutable fields can be cached/compared; status field can change
- **Domain constraints** are documented without prescribing validation mechanics

---

## Negative Scenarios

### Anti-Pattern F: Invented "Why" Not Supported by Code or Context

**Situation**: Docstring guesses at business purpose that is not discoverable from code or API boundary.

```python
# ❌ WRONG: Invented business rationale

def calculate_discount(purchase_total: float) -> float:
    """Calculate a discount to maximize customer lifetime value.

    We offer discounts to high-value customers to encourage repeat purchases
    and improve our retention metrics. This drives company profitability.

    Args:
        purchase_total: The customer's order total.

    Returns:
        float: The discount amount. Calculated to maximize customer lifetime value.
    """
    if purchase_total > 100:
        return purchase_total * 0.1
    return 0.0
```

**Why this is wrong**:
1. **Business rationale is invented**: Nothing in code signals "maximize lifetime value" or "encourage repeat purchases"
2. **Docstring couples to business strategy**: If strategy changes (e.g., "discount to prevent churn" instead), this docstring becomes stale and incorrect
3. **Caller doesn't need "why"**: Caller only needs to know "given a total, get the discount"; they don't care about business strategy
4. **Not portable**: This rationale is project-specific and not reusable in other contexts

**Correct version** (contract-only):

```python
# ✅ CORRECT: Contract-only docstring

def calculate_discount(purchase_total: float) -> float:
    """Return a discount amount for the given purchase total.

    Args:
        purchase_total: The customer's order total in dollars. Must be non-negative.

    Returns:
        float: The discount amount in dollars. Non-negative. Returned discount
            may be 0 if no discount applies.

    Example:
        >>> calculate_discount(100.0)
        10.0  # 10% discount for purchase >= $100
    """
```

---

### Anti-Pattern G: Docstring Contradicts Signature or Error Contract

**Situation**: Docstring claims one error handling behavior, but signature shows another.

```python
# ❌ WRONG: Contradictory error contract

def fetch_user(user_id: int) -> User | None:
    """Fetch a user by ID.

    Returns the user if found; raises UserNotFound if not.

    Args:
        user_id: A positive integer user ID.

    Returns:
        User | None: The user object, or None if user not found.

    Raises:
        UserNotFound: If the user does not exist.
    """
    if not self.db.exists(user_id):
        raise UserNotFound(f"User {user_id} not found")
    return self.db.get(user_id)
```

**Why this is wrong**:
1. **Contradictory behavior**: Return type says `User | None`, but docstring and implementation say raise `UserNotFound`
2. **Caller is confused**: Should I check for None or catch an exception?
3. **Violates single error-handling pattern**: Pick one (exception-based OR nullable return), not both

**Correct version** (pick one pattern):

**Option A: Exception-based**
```python
def fetch_user(user_id: int) -> User:
    """Return the user with the given ID.

    Args:
        user_id: A positive integer user ID.

    Returns:
        User: The user object.

    Raises:
        UserNotFound: If no user exists with the given ID.
    """
```

**Option B: Nullable return**
```python
def fetch_user(user_id: int) -> User | None:
    """Return the user with the given ID, or None if not found.

    Args:
        user_id: A positive integer user ID.

    Returns:
        User | None: The user object if found, or None if user does not exist.
    """
```

---

### Anti-Pattern H: Type or Error Contract Mismatch

**Situation**: Docstring describes wrong type or error behavior, misleading callers.

```python
# ❌ WRONG: Error semantics mismatch

def process_order(order_id: int) -> Result[Order, OrderError]:
    """Process an order and return the processed result.

    Returns:
        Result[Order, OrderError]: The order if successful. Error if failed.

    Raises:
        DatabaseError: If the database is unavailable.
    """
    # Implementation omits the actual error handling
```

**Why this is wrong**:
1. **Mixed error patterns**: Signature says `Result[...]` (business-return type), but docstring says `Raises:` (exception-based)
2. **Caller doesn't know how to handle errors**: Use Result or catch exception?
3. **Vague Returns description**: "The order if successful, Error if failed" is not specific (what is "Error"?)

**Correct version**:

```python
def process_order(order_id: int) -> Result[Order, OrderError]:
    """Process an order and return the result.

    Validates the order, submits to payment processor, and updates inventory.

    Args:
        order_id: A positive integer order ID.

    Returns:
        Ok(Order): On successful processing; includes transaction ID and status.
        Err(OrderError): On processing failure; includes error_code
            ('invalid_order', 'payment_declined', 'out_of_stock') and message.

    Raises:
        OrderNotFound: If no order exists with the given ID (data integrity failure).
        DatabaseError: If the database is unavailable (exceptional failure).
    """
```

This version:
- **Clearly separates error patterns**: Result[...] for expected outcomes, Raises: for exceptional failures
- **Specific about error codes**: Caller knows what to expect and how to handle each case
- **Matches signature**: Return type and docstring are aligned

---

## Summary

**Positive scenarios teach**:
- A: When "why" is explicit from boundary context, document it
- B: When "why" is not explicit, write contract-only
- C: Private helpers without independent contracts need only one-liners
- D: Private helpers with independent contracts (error translation, preconditions) need full docs
- E: Dataclass fields document semantic role without prescribing validation or type choices

**Negative scenarios teach**:
- F: Never invent business rationale not discoverable from code
- G: Never contradict signature or error contract in docstring
- H: Never describe the same error scenario using both Raises and Result; use Raises for exceptional failures and Result for expected failures
