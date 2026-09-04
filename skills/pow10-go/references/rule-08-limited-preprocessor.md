# Rule 8 — Go

Go has no preprocessor. The analogous restriction is on `unsafe`, `reflect`, and `go generate` codegen.

## Allowed

`go generate` with committed output (parser tables, mock implementations). `reflect` confined to a serialization layer. `unsafe` only behind a vetted, narrowly-scoped package boundary.

## Forbidden

`unsafe.Pointer` for type punning in safety-critical paths. `reflect` for control flow (e.g., dispatching by type at runtime). Generated code that is not committed.

## Violating example

```go
func dispatch(payload any) {
    rv := reflect.ValueOf(payload)
    method := rv.MethodByName("Handle")
    if method.IsValid() {
        method.Call(nil)
    }
}
```

Call graph hidden from static analysis; failure mode is `panic` at runtime.

## Remediation

Replace with an explicit interface and `switch`:

```go
type Handler interface {
    Handle()
}

func dispatch(payload any) error {
    h, ok := payload.(Handler)
    if !ok {
        return fmt.Errorf("dispatch: %T does not implement Handler", payload)
    }
    h.Handle()
    return nil
}
```

Type assertion is explicit; failure path is a returned error; call graph fully static.

## Hard checks

- `golangci-lint`:
  - `gosec` `G103` (audit `unsafe`)
  - `staticcheck` `SA1019` (deprecated `reflect` patterns)
- Manual review for `reflect.ValueOf(...).MethodByName(...)` and `Call`
- `go vet -unreachable` for hidden paths
