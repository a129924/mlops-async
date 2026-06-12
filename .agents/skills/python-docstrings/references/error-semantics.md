# Error Semantics: Raises vs Business-Return Patterns

## Two Patterns for Handling Errors

Python supports two fundamentally different error-handling patterns, and docstrings must document **both** patterns equally. The choice of which pattern to use is a **design decision** outside this skill's scope (that belongs to `python-model-selection` or architecture decisions). This skill teaches **how to document** each pattern.

## Pattern 1: Traditional Exception-Based (Raises:)

### Overview

Exceptions are raised when errors occur. Callers catch exceptions or let them propagate.

### Docstring Format

Use the `Raises:` section to document each exception type and the condition that triggers it.

```python
def fetch_user(user_id: int) -> User:
    """Return the user with the given ID.
    
    Args:
        user_id: A positive integer user ID.
    
    Returns:
        User: The user object.
    
    Raises:
        UserNotFound: If no user exists with the given ID.
        InvalidUserID: If user_id is not a positive integer.
        DatabaseError: If the database connection fails.
    """
```

### Key Rules

1. **List each exception type** the callable may raise
2. **Describe the condition** that triggers each exception
3. **Order by likelihood**: common errors first, then edge cases
4. **Do NOT list inherited exceptions** (e.g., don't say "Raises: Exception" if it's a base class)
5. **Be specific**: avoid vague "Raises: Error" without context

### Example: File Operations

```python
def read_file(file_path: str) -> str:
    """Return the contents of a file.
    
    Args:
        file_path: Path to the file to read.
    
    Returns:
        str: The file contents as a single string.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file is not readable due to permissions.
        IOError: If reading fails (disk error, encoding issues, etc.).
    """
```

### When to Use Raises:

- Exception handling is the **normal error path** (not an edge case)
- Callers are expected to **catch specific exceptions**
- Errors represent **failure states** (operation could not complete)
- Examples: File I/O, network requests, database operations, authentication failures

---

## Pattern 2: Business-Return Types (Result[T, E], Union[Success, Failure])

### Overview

Instead of raising exceptions, the callable returns a **tagged union** or **Result-like type** that encodes both success and failure cases. Examples: `Result[User, AuthError]`, `Union[User, None]`, `Union[User, ErrorDetails]`.

### Docstring Format

Document **both Ok and Err branches** in the `Returns:` section.

```python
from typing import Union

def authenticate(token: str) -> Union[User, AuthError]:
    """Authenticate using a token; return user or error.
    
    Args:
        token: A JWT-formatted authentication token.
    
    Returns:
        User: On successful authentication; populated with id, email, roles.
        AuthError: On authentication failure; includes error_code and message.
            Error codes: 'invalid_signature', 'expired', 'malformed_token'.
    """
```

### Key Rules

1. **Document both branches** (success and failure)
2. **Explain when each branch occurs** (What makes the operation fail?)
3. **For the Err branch, include error codes or error types** if they convey semantics
4. **Do NOT use both Raises and Returns to describe the same error case**; it is acceptable to use `Returns:` for expected business failures and `Raises:` for true exceptional failures
5. **If using generic types like Result[T, E]**, clarify what T and E represent

### Example: Result[T, E] (Rust-Like)

```python
from result import Ok, Err, Result

def create_user(name: str, email: str) -> Result[User, ValidationError]:
    """Create a user with the given name and email.
    
    Args:
        name: User's full name. Must be non-empty.
        email: User's email address. Must be valid format.
    
    Returns:
        Ok(User): On success; user object with assigned ID.
        Err(ValidationError): On failure; includes field name and error message.
            Possible error messages: 'name is empty', 'email is invalid format', 
            'email already exists'.
    """
```

### Example: Union[Success, Failure]

```python
from dataclasses import dataclass

@dataclass
class Success:
    user: User

@dataclass
class Failure:
    error_code: str
    message: str

def authenticate(token: str) -> Success | Failure:
    """Authenticate using a token.
    
    Args:
        token: A JWT authentication token.
    
    Returns:
        Success: On successful authentication; contains the authenticated User.
        Failure: On authentication failure; contains error_code ('invalid_token', 
            'expired_token', 'no_matching_user') and human-readable message.
    """
```

### When to Use Business-Return Types:

- Errors are **expected, recoverable outcomes** (not exceptional failures)
- Callers **always check the result** before using it (not just on error)
- You want **type-safe error handling** (a type checker or static analysis can enforce handling of both branches)
- Examples: Validation results, parsing attempts, optional lookups, database searches that may not find a record

---

## Comparing the Patterns

| Aspect | Exception-Based (Raises) | Result-Type (Union, Result[T,E]) |
|--------|--------------------------|-----------------------------------|
| **Error encoding** | Exception object type | Tagged union or Result generic |
| **Caller flow** | Try/catch or let propagate | Match/if on result branch |
| **Error handling** | Optional (can ignore if caller doesn't catch) | Required (result must be used) |
| **Semantics** | "Operation failed; exception occurred" | "Operation completed; here's the outcome (Ok or Err)" |
| **Docstring section** | `Raises:` | `Returns:` (document both branches) |
| **Example errors** | File not found, network error, permission denied | Validation failed, parsing failed, user not found |

---

## Mixed Scenarios: Both Patterns in One Callable

### When a callable uses BOTH patterns:

A callable may raise **exceptions for truly exceptional cases** while returning **Result-types for expected outcomes**.

```python
def process_payment(order_id: int, amount: float) -> Result[Payment, PaymentError]:
    """Process a payment for an order.
    
    Validates the order and amount, then submits to the payment processor. 
    Returns a result indicating success or business-level failure.
    
    Args:
        order_id: A positive integer order ID.
        amount: Payment amount in dollars. Must be positive.
    
    Returns:
        Ok(Payment): On successful payment processing; includes transaction ID.
        Err(PaymentError): On business-level failure (insufficient funds, 
            declined card, etc.); includes error code and recoverable message.
    
    Raises:
        OrderNotFound: If the order does not exist (data integrity failure).
        InvalidAmount: If amount is not positive (caller error).
        DatabaseError: If the database is unavailable (exceptional failure).
    """
```

**Why this works**:
- `Result[Payment, PaymentError]` documents **expected outcomes** (success or decline)
- `Raises:` documents **unexpected failures** (data corruption, configuration errors)
- Caller knows: "Handle PaymentError normally; catch exceptions for emergencies"

---

## Anti-Patterns: Error Documentation Mistakes

### ❌ Anti-Pattern 1: Vague Raises Section

```python
def delete_user(user_id: int) -> None:
    """Delete a user.
    
    Raises:
        Exception: If something goes wrong.
    """
```

**Why this is wrong**:
- "Exception" is the base class; too vague
- "If something goes wrong" doesn't specify conditions
- Caller doesn't know what to catch or how to handle it

**Better version**:
```python
def delete_user(user_id: int) -> None:
    """Delete a user.
    
    Args:
        user_id: A positive integer user ID.
    
    Raises:
        UserNotFound: If no user exists with the given ID.
        PermissionError: If the caller lacks permission to delete this user.
        DatabaseError: If the database transaction fails.
    """
```

---

### ❌ Anti-Pattern 2: Mixing Unclear Returns and Raises

```python
def find_user(user_id: int) -> User | None:
    """Find a user by ID.
    
    Raises:
        UserNotFound: If user is not found.
    """
```

**Why this is wrong**:
- Inconsistent: Returns `None` for not-found, but also raises `UserNotFound`?
- Caller is confused: Should I check `None` or catch the exception?
- Violates single error-reporting pattern

**Better version** (pick one):

**Option A: Returns-based**
```python
def find_user(user_id: int) -> User | None:
    """Return the user with the given ID, or None if not found."""
```

**Option B: Exception-based**
```python
def find_user(user_id: int) -> User:
    """Return the user with the given ID.
    
    Raises:
        UserNotFound: If no user exists with the given ID.
    """
```

---

### ❌ Anti-Pattern 3: Not Documenting Error Codes in Result Types

```python
def validate_email(email: str) -> Result[Email, ValidationError]:
    """Validate an email address."""
```

**Why this is wrong**:
- `ValidationError` is generic; caller doesn't know what errors are possible
- Caller can't handle specific validation failures (format vs already-exists)

**Better version**:
```python
def validate_email(email: str) -> Result[Email, ValidationError]:
    """Validate an email address.
    
    Returns:
        Ok(Email): On successful validation; email is well-formed and unique.
        Err(ValidationError): On validation failure; includes error_code 
            ('invalid_format', 'too_long', 'already_exists') and message.
    """
```

---

## Design Philosophy (Not Prescriptive)

This skill teaches **how to document** errors, not **which pattern to choose**. However, here are design heuristics (not rules):

- **Use exceptions** when errors are rare and represent exceptional failure (network error, file not found)
- **Use Result-types** when errors are expected and part of normal operation (validation failure, not-found on optional lookup)
- **Never mix** both patterns for the same outcome (don't raise AND return error for the same case)
- **Document clearly** so callers know what to expect and how to handle each outcome
