# Rule 9 — C

## Forbidden

`**` and `***` in declarations (more than one level of indirection). Function pointer types, typedefs, and assignments.

## Allowed (with documented waiver, isolated)

Hardware interrupt vector tables. `argv` (`char **` is part of the C standard signature for `main`).

## Violating example

```c
typedef int (*handler_t)(event_t *);

static handler_t handlers[NUM_EVENTS];

void dispatch(event_t *e) {
    handlers[e->type](e);
}
```

Function pointer table defeats call-graph analysis; reachability of any specific handler is hidden.

## Remediation

Replace with a `switch`:

```c
void dispatch(event_t *e) {
    assert(e != NULL);
    switch (e->type) {
        case EVT_HEARTBEAT: handle_heartbeat(e); break;
        case EVT_COMMAND:   handle_command(e);   break;
        case EVT_TELEMETRY: handle_telemetry(e); break;
        default:
            panic("dispatch: unknown event type %d", e->type);
    }
}
```

Call graph fully static. `default` panics on unhandled types — fail fast.

## Hard checks

- `clang-tidy`: no built-in matcher for `**` count; write a custom `clang-query` rule
- `cppcheck` for function-pointer warnings (`functionConst`, `functionStatic`)
- Manual review of declarations
