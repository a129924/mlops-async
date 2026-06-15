# API client porting implementer examples

## Example 1: single safe API

Good implementation pattern:

1. Re-read the source lines and confirm request behavior.
2. Add a request test that checks method, path, required header subset, query key-value semantics, and body shape.
3. Implement only the async behavior needed for the request test.
4. Add a tolerant response model that ignores or allows unknown fields.
5. Add response and error tests from observed fixtures or documented behavior.
6. Mark response compatibility `normalized` if converting raw JSON into a typed model.
7. Update in-scope trackers or emit tracker-ready handoff content.
8. Finish with `continue` or `stable`.

Bad implementation pattern:

- implement the method before request tests exist
- assert the full raw query string order
- mark response compatibility `equivalent` after returning a typed model
- skip tracker-ready output because tests pass

## Example 2: safe same-family batch

Good implementation pattern:

- reconfirm source evidence for each API instead of copying blindly
- reuse request-test structure only within the same endpoint family
- keep response schema conservative unless fixtures prove more
- create one tracker-ready result per API when canonical tracker files are absent

Bad implementation pattern:

- apply the pattern to a different family because names look similar
- batch an API with pagination expansion, conditional endpoint selection, or global session side effects

## Example 3: blocked or needs-human-review

Correct outcome:

- do not implement automatically when source behavior includes job wait, polling, or unclear response behavior
- record the uncertainty
- emit a tracker-ready result with compatibility `unknown` when appropriate
- finish with `needs-human-review` or `blocked`
