# Rule 4 — C

## Limits

Hard 60 source lines per function (excluding comments). Soft 40. Cyclomatic complexity ≤ 10.

## Violating example

```c
int process_request(request_t *req, response_t *resp) {
    /* validate (20 lines) */
    if (req == NULL) return -1;
    if (req->len > MAX_LEN) return -2;
    /* ... 18 more lines ... */
    /* parse (20 lines) */
    parser_t p;
    parser_init(&p, req->body);
    /* ... 18 more lines ... */
    /* execute (15 lines) */
    /* ... */
    /* serialize response (15 lines) */
    /* ... */
    return 0;
}
```

70+ lines, four distinct responsibilities, untestable as a unit.

## Remediation

Decompose by responsibility — each new function fits on a page:

```c
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

Each helper is independently testable; `process_request` is now ~10 lines.

## Hard checks

- `clang-tidy`: `readability-function-size` with `LineThreshold: 60`, `StatementThreshold: 50`
- `lizard` for cyclomatic complexity
