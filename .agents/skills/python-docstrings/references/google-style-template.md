# Google Style Template

## Format Overview

Google Style docstrings follow a structured, readable format optimized for clarity. The format is widely adopted in industry and supports both traditional exception-based and modern business-return patterns.

## Structure

```
"""One-liner summary (present tense, end with period).

Extended description explaining intent, boundary context, preconditions, or 
domain semantics. This section is optional if the one-liner is self-evident.

Args:
    param_name (type, optional): Description of parameter role and any constraints.
    another_param: Can omit type if signature already declares it.

Returns:
    type: Description of return value, including optional/error semantics.

Raises:
    ExceptionType: When and why this exception is raised.
    AnotherException: Conditions that trigger this error.

Example:
    Typical use case with code snippet showing how to call the function.

Yields:
    type: For generators; describes each yielded value.
"""
```

## Section Details

### One-Liner (Required)

- Present tense, active voice: "Authenticate a user..." not "This method authenticates..."
- End with a period
- Convey the callable's **main purpose** in one sentence
- Keep it short (under 80 characters if possible)

**Examples**:
- ✅ "Authenticate a user using a JWT token."
- ✅ "Build a database query filter for the given role."
- ❌ "Returns a User object" (too implementation-focused)
- ❌ "This method is important for authentication" (too vague)

### Extended Description (Optional)

- Explain **why** the callable exists, **when** to use it, or **what contract** it enforces
- Note preconditions not obvious from signature (e.g., "Requires a valid JWT secret")
- Mention boundary context if relevant (e.g., "Primary authentication entry point for REST API")
- Do NOT explain line-by-line how the code works; that's what code review is for
- Keep it concise; 2–3 sentences usually suffice

**Example**:
```python
def authenticate_user(token: str, secret_key: str) -> User:
    """Authenticate a user using a JWT token.
    
    Verifies the JWT signature against the provided secret key and extracts the 
    embedded user identity. This is the primary authentication entry point for 
    REST API requests.
    """
```

### Args (Include if method accepts parameters)

- List each parameter name and its purpose
- Type is optional (signature already declares it); use type only if docstring adds semantic clarity
- Describe constraints, valid ranges, or domain meaning
- For `*args` and `**kwargs`, describe their expected structure

**Example**:
```python
Args:
    token: A JWT-formatted bearer token from the request Authorization header.
    secret_key: The HMAC secret key used to verify the token signature.
    timeout_seconds: Max seconds to wait for external validation. Defaults to 5.
    skip_verification: If True, bypass signature verification (use only in tests).
```

### Returns (Include if callable returns a value)

- Always document non-None returns; optional to document if return is always None
- Describe the return **meaning**, not just the type
- If returning multiple types (e.g., `Union[User, None]`), clarify which is success and which is error
- If using business-return patterns (e.g., `Result[T, E]`), explain both Ok and Err branches in the Returns section

**Example**:
```python
Returns:
    User: A user object with populated id, email, and roles extracted from token claims.
    
    Result[User, AuthError]: For result-type returns, Ok(user) on successful
        authentication; Err(auth_error) on failure.
```

### Raises (For exception-based error handling)

- List each exception type that the callable may raise
- Explain the **condition** that triggers each exception
- Be specific; avoid "Raises: Exception" or vague "May raise errors"

**Example**:
```python
Raises:
    JWTError: If the token signature is invalid or the token is expired.
    ValueError: If the token is malformed or missing required claims.
    KeyError: If the secret key is not found in the configuration store.
```

### Example (Recommended for public API)

- Show 1–2 typical use cases
- Include code snippet if the usage is non-obvious
- Keep examples short and self-contained

**Example**:
```python
Example:
    Authenticate a user and retrieve their data:
        user = authenticate_user(token="eyJ0...", secret_key="secret123")
        print(user.email)
```

### Yields (For generators)

- Similar to Returns, but for each yielded value
- Describe the type and semantic meaning

**Example**:
```python
Yields:
    User: Each authenticated user from the batch token list.
```

## Special Patterns

### Class Docstrings

```python
class UserRepository:
    """Repository for User entities.
    
    Provides CRUD operations and query methods for users. Encapsulates database 
    access patterns and maintains transaction semantics.
    
    Attributes:
        db_connection: Active database connection.
        cache_enabled: Whether query results are cached.
    
    Example:
        repo = UserRepository(db_connection)
        user = repo.get_by_id(42)
    """
```

### Module-Level Docstrings

```python
"""Authentication utilities for JWT-based API access.

This module provides functions for issuing, validating, and refreshing JWT tokens.
It is the primary entry point for authentication in REST API handlers.
"""
```

### Dataclass Field Docstrings

```python
from dataclasses import dataclass

@dataclass
class User:
    """A user identity in the system."""
    
    id: int
    """Unique user identifier. Primary key in the users table."""
    
    email: str
    """User email address. Must be unique across all users."""
    
    roles: list[str]
    """List of role names (e.g., 'admin', 'editor'). Empty list if no roles assigned."""
```

## Formatting Rules

1. **Indentation**: Use consistent indentation (usually 4 spaces)
2. **Line length**: Keep lines under 88 characters for readability
3. **Empty lines**: Use blank lines between sections (Args, Returns, Raises)
4. **Code in docstrings**: Use triple backticks ` ``` ` with language hint (e.g., ` ```python `)
5. **References**: Link to related functions using backticks (e.g., `see_related_function`)

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Over-explaining obvious | "Returns a string that represents..." | Just say what the string means |
| Invented rationale | "For business reporting purposes" (not in code/API) | State the contract only |
| Type redundancy | "str: Returns a string value" | Omit the type (already in signature) |
| Vague Returns | "Returns: The result" | Describe what "result" means |
| Missing error docs | No Raises section when exceptions occur | Explicit error contract required |
| Implementation detail | "Loops through the list to find..." | Not what docstring is for |
