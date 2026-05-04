---
name: python-docstrings
description: Write clear, contract-first docstrings using Google Style format with explicit intent and boundaries
---

# Python Docstrings

## Purpose

Guide developers to write clear, contract-first docstrings in Google Style format that emphasize **explicit over implicit**. Docstrings should capture callable intent, boundary semantics, and error contracts so code is self-documenting without invented rationale.

## Trigger / When to use

**Use this skill when**:
- Writing or reviewing public API docstrings (classes, public methods, module-level functions, dataclass fields)
- Deciding when a private helper method needs more than a one-liner
- Choosing between traditional `Raises:` vs business-return patterns (e.g., `Result[T, E]`)
- Documenting semantic intent without guessing at hidden business rationale
- Capturing error semantics and field-level contracts in structured data

**Do NOT use this skill for**:
- Choosing type hint shapes (e.g., `Optional` vs `Union`) — delegate to `python-type-hints-strict`
- Deciding whether to use a dataclass, ABC, or enum — delegate to `python-model-selection`
- Naming conventions — delegate to `python-naming`
- Framework-specific auto-docs (FastAPI, Pydantic, SQLAlchemy) — out of scope
- Inline comments on algorithms or control flow — delegate to code clarity improvements

## Inputs

- Public or private method/class/function signature with type hints
- Explicit code-adjacent context: parameter names, return types, error types, module/class role, surrounding API boundary
- Business contract signals: what callers need to know about preconditions, postconditions, error paths, or domain semantics

## Process

**Step-by-step docstring workflow**:

1. **Identify scope**: Is this a public API (class, public method, public function, dataclass field) or private helper?
   - **Public**: Always write a full Google Style docstring (one-liner + description + applicable sections such as Args/Returns/Raises/Examples as needed)
   - **Private**: Write one-liner; add full docstring only if explicit contract signals exist (state mutation, error translation, structured/domain return, reused preconditions)

2. **Extract explicit signals**:
   - Symbol name and module/class role
   - Parameter names and type annotations
   - Return type (including `None`)
   - Named error types (exception classes, `Result`, `Union[Success, Failure]`)
   - Constraints visible in code (e.g., guards, validators)

3. **Derive semantic intent**:
   - If signals reveal a clear boundary or domain role (e.g., "authenticate a user against JWT"), document that **why** and **when** briefly
   - If signals do **not** reveal trustworthy "why", skip invented rationale and write contract-only docstring instead
   - When in doubt, prefer **"what contract / when to call"** over speculative "why"

4. **Identify error paths**:
   - Traditional: document exception types in `Raises:` and when they occur
   - Modern: if returning `Result[T, E]` or `Union[Success, Failure]`, document both Ok and Err paths in `Returns:` section
   - For dataclass fields: document domain constraints only if they are already explicit in public API or validation

5. **Fill Google Style sections**:
   - **One-liner**: callable purpose in present tense (e.g., "Authenticate a user using JWT.")
   - **Extended description**: intent, boundary context, preconditions (if not obvious from signature)
   - **Args**: parameter purpose, type (optional; trust signature), constraints
   - **Returns**: return value meaning, optional/error semantics
   - **Raises** or error case in `Returns:`: when and why exceptions/errors occur
   - **Examples**: 1–2 typical use cases (optional for simple callables)
   - **Yields** (if generator): similar to Returns

## Examples

### ✅ Positive Example: Contract-First Docstring with Explicit Boundary

```python
def authenticate_user(token: str, secret_key: str) -> User:
    """Authenticate a user using a JWT token.
    
    Verifies signature against the secret key and extracts user identity.
    Primary entry point for REST API authentication.
    
    Args:
        token: JWT-formatted bearer token from Authorization header.
        secret_key: HMAC secret key to verify token signature.
    
    Returns:
        User object with id, email, and roles from token claims.
    
    Raises:
        JWTError: Token signature invalid or expired.
        ValueError: Token malformed or missing required claims.
    """
```

**Why correct**: Captures **why** and **when** from explicit context (function name, parameters, return type, exception types). No invented rationale.

---

### ❌ Negative Example: Invented Rationale and Speculation

```python
def process_order(order_id: int) -> Order:
    """Process an order to generate revenue for the platform.
    
    This is important for business growth. Called from payment service 
    during checkout.
    
    Args:
        order_id: The order ID. It's a number.
    
    Returns:
        An Order object. Main data structure.
    
    Raises:
        OrderNotFound: Probably from user deletion or race condition.
    """
```

**Why wrong**: (1) Invented rationale not in code, (2) Over-explains obvious, (3) Speculates on error causes, (4) Restates type info

---

## Outputs

A complete Google Style docstring following the contract-first philosophy:
- Clear one-liner summarizing intent
- Extended description only when intent is explicit from code-adjacent context
- Args / Returns / Raises sections that state the contract clearly
- No invented business rationale not discoverable from code or surrounding API
- Portable; no project-specific architecture assumptions

## Boundaries

**OUT of scope** (delegate to other skills):
- Type hint shape decisions (`Optional` vs `Union`, `int` vs `float`) → `python-type-hints-strict`
- Model and class design choices (dataclass vs ABC, @validator, JSONSchema) → `python-model-selection`
- Naming conventions for identifiers and variables → `python-naming`
- Framework-specific docstring patterns (FastAPI auto-docs, Pydantic, SQLAlchemy) → framework skills
- Linting and auto-formatting → linter configuration
- Async/await specific patterns → future skill (explicitly deferred)
- Deprecation warnings and version history → future skill (explicitly deferred)

**IN scope** (this skill owns):
- Google Style format and structure (one-liner, description, Args/Returns/Raises/Examples/Yields)
- Public API contract documentation (classes, public methods, public functions, dataclass fields)
- Private method docstring rule (one-liner vs full, based on independent contract signals)
- Semantic intent capture (derivation method from explicit signals; contract-only fallback)
- Error semantics (both traditional `Raises:` and business-return patterns like `Result[T, E]`)
- Dataclass field-level semantic documentation
- Type hint alignment (docstrings must not contradict signatures)

## Local references

- **reference.md**: Navigation overview; lists split reference files and their roles
- **references/google-style-template.md**: Google Style structure reference and format guidelines
- **references/semantic-intent.md**: How to derive semantic intent from explicit signals; fallback rules; anti-pattern examples
- **references/error-semantics.md**: Traditional `Raises:` vs business-return patterns (Result[T,E]); error documentation without choosing design pattern
- **references/dataclass-patterns.md**: Field-level documentation; semantic role capture; contract-vs-validation boundary
