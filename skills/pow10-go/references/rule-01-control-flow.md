# Rule 1 — Go

## Forbidden

`goto` (rare but exists), direct or indirect recursion. `defer` for cleanup is allowed and preferred over `goto cleanup` patterns.

## Violating example

```go
func walk(n *Node, visit func(*Node)) {
    if n == nil {
        return
    }
    visit(n)
    walk(n.Left, visit)
    walk(n.Right, visit)
}
```

Recursive tree walk. Stack depth unbounded.

## Remediation

Iterate with an explicit bounded stack:

```go
const maxDepth = 1024

func walk(root *Node, visit func(*Node)) {
    stack := make([]*Node, 0, maxDepth)
    stack = append(stack, root)
    for i := 0; i < maxDepth && len(stack) > 0; i++ {
        n := stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        if n == nil {
            continue
        }
        visit(n)
        stack = append(stack, n.Right, n.Left)
    }
}
```

Stack capacity caps reachable depth; the `for` loop carries an explicit upper bound (Rule 2).

## Hard checks

- `golangci-lint` with `gocyclo`, `nestif`, `gocritic`
- No standard recursion check; manual review or custom `analysis.Analyzer`
