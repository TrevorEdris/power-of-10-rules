# Rule 4 - Short Functions (C)

**Statement (Holzmann):** Each function fits on one printed page - hard limit 60 source lines (excluding comments), soft limit 40.

**Profile (literal):** applies fully; severity **high**.

Flight software requires a function be fully visible to one reviewer without scrolling or paging. A function that exceeds the page-fit limit hides mixed responsibilities and defeats unit testability. Line-count alone is Holzmann's original test; complexity metrics are a reasonable but separate, uncited addition used here as a supporting smell signal.

## Checklist
- Count source lines excluding comments; flag functions over 60, review functions over 40.
- Verify the function has one responsibility, not validate+parse+execute+serialize combined.
- Check nesting depth stays at or under 3 levels of `if`/`for`/`while`.
- Confirm each candidate helper can be extracted and unit-tested without the whole call chain.
- Reject `switch` dispatchers over the limit unless they are table-driven.

## Violation

```c
/* types and helper prototypes elided */
int process_request(request_t *req, response_t *resp) {
    if (req == NULL) return -1;
    if (req->len > MAX_LEN) return -2;
    if (req->body == NULL) return -3;
    parser_t p;
    parser_init(&p, req->body);
    if (parser_run(&p) != 0) return -4;
    result_t result;
    if (execute(&p, &result) != 0) return -5;
    if (serialize_response(&result, resp) != 0) return -6;
    return 0;
}
```

## Fix

```c
/* types and helper prototypes elided */
int process_request(request_t *req, response_t *resp) {
    int rc = validate_request(req);
    if (rc != 0) return rc;
    parsed_t parsed;
    rc = parse_request(req, &parsed);
    if (rc != 0) return rc;
    result_t result;
    rc = execute(&parsed, &result);
    if (rc != 0) return rc;
    return serialize_response(&result, resp);
}
```

## Tooling
- `clang-tidy`: `readability-function-size` with `LineThreshold: 60` and `StatementThreshold: 50` - flags functions over the line/statement cap
- `manual review`: confirm each function has one responsibility and nesting stays under 3 levels; no automated tool catches mixed-responsibility bodies

## Strict profile
STRICT CI treats the 60-line/40-statement cap as a literal, build-blocking gate via `clang-tidy readability-function-size` (or `lizard`) with zero exceptions - flight software has no post-ship refactor path, so nothing merges over the limit.
