# API client porting implementer examples

## Example 1: single safe API

Input:

- Planner output identifies `source_sdk.widgets.get_widget`
- Source evidence includes file, line range, commit, method `GET`, path `/widgets/{widget_id}`, required `Accept` header, query key `includeDetails`, and no body
- Response fixture shows JSON object with stable `id`, `name`, and extra server fields

Good implementation pattern:

1. Re-read the source lines and confirm request behavior.
2. Add a request test that checks method, path, required header subset, query key-value semantics, and no body.
3. Implement only the async `get_widget` behavior needed for the request test.
4. Add a tolerant response model with `extra="ignore"` or `extra="allow"`.
5. Add response and error tests based on observed fixtures or documented source behavior.
6. Mark response compatibility `normalized` if converting raw JSON into a typed Pydantic model.
7. Update the ledger and finish with `continue` or `stable`.

Bad implementation pattern:

- Implement the method before request tests exist.
- Assert the full raw URL query string order.
- Mark response compatibility `equivalent` after returning a typed model instead of raw SDK output.
- Skip the ledger because tests pass.

## Example 2: safe same-family batch

Input:

- Two `folders` family APIs already have passing request contract tests.
- A third `folders` read-only API uses the same auth, path prefix, and query semantics.
- No stop flags are present.

Good implementation pattern:

- Reconfirm source evidence for the third API instead of copying blindly.
- Reuse the same request-test structure within the endpoint family.
- Keep response schema conservative unless fixtures prove more.
- Create or update a ledger entry for each API in the batch.

Bad implementation pattern:

- Apply the pattern to a different endpoint family because names look similar.
- Batch an API with pagination expansion, conditional endpoint selection, or global session side effects.

## Example 3: blocked or needs-human-review

Input:

- Source function wraps a job submission and waits for completion.
- The request path is visible, but retry and polling behavior are embedded in helper calls.
- Response schema changes depending on job state.

Correct outcome:

- Do not implement the method automatically.
- Record source evidence and the uncertainty.
- Emit or update a ledger entry with compatibility label `unknown` where appropriate.
- Finish with `needs-human-review` if a human can decide scope, or `blocked` if the request contract itself is unsafe.

Incorrect outcome:

- Implement only the initial POST request and ignore polling.
- Claim compatibility with the source SDK while dropping wait behavior.
- Omit the stop condition from the final handoff.
