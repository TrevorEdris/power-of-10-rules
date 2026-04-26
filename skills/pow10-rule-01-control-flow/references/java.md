# Rule 1 — Java

## Forbidden

Direct or indirect recursion. Labeled `break` and `continue` (Java's nearest equivalent to `goto`).

## Violating example

```java
void walk(Node n, Consumer<Node> visit) {
    if (n == null) return;
    visit.accept(n);
    walk(n.left, visit);
    walk(n.right, visit);
}
```

Recursive descent. Default JVM thread stack (512 KB on HotSpot) overflows at a few thousand frames.

## Remediation

Iterate with a bounded `ArrayDeque`:

```java
private static final int MAX_NODES = 10_000;

void walk(Node root, Consumer<Node> visit) {
    Deque<Node> stack = new ArrayDeque<>(MAX_NODES);
    stack.push(root);
    for (int i = 0; i < MAX_NODES && !stack.isEmpty(); i++) {
        Node n = stack.pop();
        if (n == null) continue;
        visit.accept(n);
        stack.push(n.right);
        stack.push(n.left);
    }
    if (!stack.isEmpty()) {
        throw new IllegalStateException("walk exceeded " + MAX_NODES + " nodes");
    }
}
```

The loop's explicit `MAX_NODES` cap satisfies Rule 2; the post-condition asserts the cap held.

## Hard checks

- `Checkstyle`: `AvoidNestedBlocks`, `MissingSwitchDefault`
- `PMD`: `AvoidDeeplyNestedIfStmts`, `CyclomaticComplexity`
- `SpotBugs`: custom detector for recursion, or manual review
