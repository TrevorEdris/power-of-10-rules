# Rule 1 — Kotlin

## Forbidden

Direct or indirect recursion — including `tailrec`. Tail-call optimization eases stack pressure but still complicates reasoning for safety review. Labeled returns (`return@label`) used as control-flow shortcuts.

## Violating example

```kotlin
tailrec fun walk(node: Node?, visit: (Node) -> Unit) {
    if (node == null) return
    visit(node)
    walk(node.next, visit)
}
```

Even with `tailrec`, the call graph reads as a recursion to a reviewer.

## Remediation

Rewrite as an iterative loop with an explicit cap:

```kotlin
private const val MAX_NODES = 10_000

fun walk(start: Node?, visit: (Node) -> Unit) {
    var node = start
    repeat(MAX_NODES) {
        if (node == null) return
        visit(node!!)
        node = node!!.next
    }
    error("walk exceeded $MAX_NODES nodes")
}
```

`repeat(MAX_NODES)` satisfies Rule 2; `error` triggers a defined recovery if the cap is exceeded.

## Hard checks

- `detekt`: `LabeledExpression`, `ReturnFromFinally`, `LongMethod`
- Custom `detekt` rule for direct/indirect recursion if available
