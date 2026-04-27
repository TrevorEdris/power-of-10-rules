# Rule 10 — Kotlin

## Required

`kotlinc -Werror -Xjvm-default=all` plus opt-in warnings. `detekt` with `--build-upon-default-config` plus a strict project ruleset. `ktlint` for style. For mixed-JVM projects, also run Error Prone.

## Violating example

```kotlin
// build.gradle.kts: no strictness
kotlin {
    jvmToolchain(17)
}
```

Warnings non-fatal; lint absent.

## Remediation

```kotlin
// build.gradle.kts
kotlin {
    jvmToolchain(17)
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        allWarningsAsErrors = true
        freeCompilerArgs = listOf(
            "-Xjsr305=strict",
            "-Xjvm-default=all",
            "-opt-in=kotlin.RequiresOptIn",
        )
    }
}

plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.1"
}

detekt {
    buildUponDefaultConfig = true
    config.setFrom("$projectDir/detekt.yml")
    allRules = false  // start strict but not exhaustive
}

tasks.named("check") {
    dependsOn("detekt", "ktlintCheck")
}
```

CI:

```yaml
- run: ./gradlew check
```

Any compiler warning, detekt finding, or ktlint violation fails the build.

## Suppressions

```kotlin
@Suppress("UNCHECKED_CAST")  // pow10: allow rule=10 until=2026-12-31 owner=team reason="legacy generic API"
val result = legacy.getResult() as List<String>
```
