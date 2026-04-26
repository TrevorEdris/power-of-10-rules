# Rule 2 — Java

## Forbidden

`while (true)` without an internal counter check. `for (;;)` without a justification waiver.

## Violating example

```java
void consume(BlockingQueue<Msg> queue) throws InterruptedException {
    while (true) {
        Msg m = queue.take();
        process(m);
    }
}
```

Termination depends entirely on external thread interrupt; not statically bound.

## Remediation

```java
private static final int MAX_BATCH = 256;

void consume(BlockingQueue<Msg> queue) throws InterruptedException {
    for (int i = 0; i < MAX_BATCH; i++) {
        Msg m = queue.poll(100, TimeUnit.MILLISECONDS);
        if (m == null) return;
        process(m);
    }
}
```

Counter caps iterations; `poll` with timeout caps wait per iteration.

## Hard checks

- `PMD`: `WhileLoopWithLiteralBoolean`, `AvoidBranchingStatementAsLastInLoop`
- `SpotBugs`: infinite-loop detector
- `Error Prone`: `InfiniteRecursion` (related)
