# Rule 10 — Java

## Required

`javac -Xlint:all -Werror`. Run all of: Error Prone (compile-time), SpotBugs (bytecode), Checkstyle (style/structure), and one of NullAway / Checker Framework for nullability.

## Violating example

```xml
<!-- pom.xml: builds without strictness -->
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <source>17</source>
    <target>17</target>
  </configuration>
</plugin>
```

No `-Xlint`; warnings silently swallowed.

## Remediation

```xml
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <source>17</source>
    <target>17</target>
    <compilerArgs>
      <arg>-Xlint:all</arg>
      <arg>-Werror</arg>
      <arg>-XDcompilePolicy=simple</arg>
      <arg>-Xplugin:ErrorProne -XepDisableWarningsInGeneratedCode</arg>
      <arg>-processorpath</arg>
      <arg>${com.google.errorprone:error_prone_core:jar}</arg>
    </compilerArgs>
  </configuration>
</plugin>

<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <executions>
    <execution>
      <goals><goal>check</goal></goals>
    </execution>
  </executions>
</plugin>

<plugin>
  <artifactId>maven-checkstyle-plugin</artifactId>
  <configuration>
    <failOnViolation>true</failOnViolation>
    <configLocation>checkstyle.xml</configLocation>
  </configuration>
</plugin>
```

CI step:

```yaml
- run: mvn -B verify  # compile + tests + spotbugs + checkstyle
```

Any failure aborts.

## Suppressions

```java
@SuppressWarnings("unchecked")  // pow10: allow rule=10 until=2026-12-31 owner=team reason="legacy generic API"
List<String> result = (List<String>) legacy.getResult();
```

Forbid `@SuppressWarnings` without an adjacent `// reason:` (Checkstyle custom rule).
