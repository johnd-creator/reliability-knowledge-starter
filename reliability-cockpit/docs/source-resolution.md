# Source Resolution Pattern

Example application request:

```text
Need:
- equipment hierarchy
- 3-year maintenance history
- failure history
- bearing temperature
- vibration
- MW
- running status
```

Resolution:

```text
Equipment hierarchy   -> Maximo Knowledge
Maintenance history   -> Maximo Knowledge
Failure history       -> Maximo Knowledge
Bearing temperature   -> PI Knowledge
Vibration             -> PI Knowledge
MW                    -> PI Knowledge
Running status        -> PI Knowledge
```

The application should receive normalized contracts rather than raw vendor payloads.
