# Design

## Context

Greenfield repository: the only content today is the OpenSpec workspace (`openspec/`) and
the agent configuration (`.opencode/`). There is no source tree, no packaging metadata and
no CI yet.

Constraints that shape this design:

- The deliverable is a **library**, consumed as a dependency by the hotel revenue team's
  own Python scripts. No server, no HTTP API, no database, no UI.
- The library code may only use the standard library (`datetime`, `decimal`). `pytest` is
  needed to run the suite, inside the container and on a developer machine.
- The team executing the change is a **single Developer agent**: there is no QA role and
  no DevSec role, so the same Developer writes the implementation and the tests.
- The project is always delivered containerized: a root `Dockerfile` and a root
  `docker-compose.yml`. The delivery environment has **no Docker daemon**, so the
  container files are reviewed statically (the compose file must parse as YAML and every
  `COPY` source must exist) rather than by running `docker build` / `docker compose up`.
- The behaviour contract is fixed by the specs in `specs/`; this document only describes
  how it is built.

## Goals / Non-Goals

**Goals:**

- One small module with three public functions (`nights`, `nightly_rate`, `stay_total`)
  that the revenue team can import and trust.
- Monetary values computed with `Decimal` end to end, with a single, explicit rounding
  rule (`ROUND_HALF_UP` to 2 decimals).
- Input validation that fails fast and predictably: type problems raise `TypeError`,
  value problems raise `ValueError`.
- A test suite that exercises the public behaviour only, written by the Developer.
- A reproducible container that installs the dependencies, runs the suite and exits.

**Non-Goals:**

- No HTTP server, REST endpoints, background jobs, database or persistence layer.
- No configuration files, environment variables, feature flags or pricing tables loaded
  from outside the module — rates and capacities are constants of the library.
- No multi-currency support, no tax jurisdiction logic beyond the flat tourist tax.
- No CLI entry point: the consumer is other Python code.
- No DevSec pipeline, container scanning or CI workflow (no QA/DevSec roles exist on the
  team).

## Decisions

### D1 — Single module `src/booking.py` with three public functions

The library is one file, `src/booking.py`, exposing exactly `nights`, `nightly_rate` and
`stay_total`. Helpers stay private (leading underscore): `_require_date`, `_require_guests`,
`_rate_for_room`, `_capacity_for_room`, `_money`, `_night_sequence`.

*Rationale:* the request asks for a small library in that exact path, and three cohesive
functions belong to a single domain (pricing a stay).

*Alternative considered:* a package `src/booking/__init__.py` re-exporting submodules
(`pricing.py`, `validation.py`). Rejected: it adds a directory level and import ceremony
for a handful of functions, and the revenue team's imports would change without any
behavioural gain.

### D2 — `Decimal` literals and a single quantization helper

All amounts are `decimal.Decimal` built from string literals (`Decimal("50.00")`,
`Decimal("2.50")`, `Decimal("0.25")`, `Decimal("0.10")`), never from floats. A private
`_money(value)` helper applies `value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

*Rationale:* binary floats cannot represent `0.10` or `1.25` exactly, so percentage
surcharges and discounts would drift. `Decimal` + one rounding point keeps results
reproducible for the same inputs on every machine.

*Alternative considered:* integer cents as the internal representation. Rejected: it
complicates the public API (the contract requires `Decimal` results) without adding
value at this size.

### D3 — Date validation accepts only plain `datetime.date`

`_require_date(value, name)` accepts an instance of `datetime.date` **only if** it is not
an instance of `datetime.datetime` (`datetime` is a subclass of `date`, so the subclass
must be rejected explicitly) and raises `TypeError` otherwise. The type guard runs before
any comparison, so a non-date argument can never surface as a comparison error.

*Rationale:* the request distinguishes "not a date" and "a datetime" as two `TypeError`
cases; checking the subclass explicitly is the only way to honour that distinction while
still accepting `date` instances.

*Alternative considered:* accepting `datetime` and truncating it to its date. Rejected: it
would silently change the meaning of a timestamp argument.

The same guard is applied to the `day` argument of `nightly_rate`, for consistency within
the module. This consistency guard is a design choice, not a specified behaviour.

### D4 — Validation order inside `stay_total`

The order is fixed so that error types are deterministic when several inputs are invalid
at once:

1. `check_in` / `check_out` type guard → `TypeError`.
2. `check_out` must be after `check_in`, and the stay must be at most 30 nights →
   `ValueError` (computed by `nights`).
3. `guests` type guard (`int` and not `bool`) → `TypeError`.
4. Room type lookup (rate and capacity) → `ValueError` for an unknown room.
5. `guests` range check, `1 <= guests <= capacity` → `ValueError`.

*Rationale:* all `TypeError` conditions are resolved before any `ValueError` condition,
so a malformed argument never hides behind a value error, and callers can rely on
`TypeError` meaning "wrong shape of input".

*Alternative considered:* validating the room before the guests. Rejected: the capacity
is only meaningful for a known room, and deferring the capacity check keeps the
guest-count error close to the guest-count type error.

### D5 — `stay_total` composes already-rounded night rates

`stay_total` iterates the nights with `nightly_rate`, so every night contributes the
2-decimal rate that the pricing rules define; those values are summed into the **room
subtotal**. When the stay is 7 nights or longer, 10% is subtracted from the room subtotal
only. The tourist tax is then added: `2.50 x guests x nights`. The final sum is quantized
once with `_money`.

*Rationale:* the discount is defined on the room subtotal and never on the tax, and only
the final result is specified as rounded — so intermediate values are left at full
precision and rounded exactly once at the end.

*Alternative considered:* quantizing the discounted subtotal before adding the tax.
Rejected: the request rounds the *result*, not each intermediate step.

### D6 — Weekend surcharge is keyed on the start-of-night weekday

`day.weekday()` returns `4` for Friday and `5` for Saturday; those two nights get
`base x 1.25`. All other nights (Sunday through Thursday) get the base rate. The rule is
about the day the night *starts*, so the Friday night of a stay is surcharged and the
Sunday night is not.

*Alternative considered:* charging the surcharge to the night that *ends* on a Friday or
Saturday. Rejected: the request says "the night that starts on `day`".

### D7 — Room types are exact, case-sensitive string identifiers

The three supported identifiers are `single`, `double` and `suite`, stored in two module
constants: `BASE_RATES` (per-night price) and `ROOM_CAPACITY` (`single` 1, `double` 2,
`suite` 4). Any other identifier — including a differently cased one such as `Single`, an
empty string or a non-string — is an unknown room and raises `ValueError`.

*Alternative considered:* normalising case before lookup. Rejected: it would make
`"SINGLE"` a valid room, which the request does not ask for, and would hide typos in the
consumer's own data.

### D8 — Packaging with `pyproject.toml` using a src layout

`pyproject.toml` declares the project with setuptools, `package-dir = {"" = "src"}` and
`py-modules = ["booking"]`, so `pip install .` exposes the module as `booking` and the
revenue team's scripts read `from booking import nights, nightly_rate, stay_total`. It
also carries the pytest configuration:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

`pythonpath = ["src"]` lets the suite run straight from a checkout without installing
the package, which is what the container does.

*Rationale:* the library is consumed "as a dependency in their Python scripts"; the
src layout keeps the importable package separate from the repository root and makes the
`src/` path meaningful.

*Alternative considered:* leaving the project uninstallable and importing it as
`src.booking`. Rejected: `src` would become the package name, which is a poor public
name for a dependency.

### D9 — Container: one image that runs the suite, one compose service that builds it

`Dockerfile` (repository root):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pytest

COPY src/ ./src/
COPY tests/ ./tests/
COPY pyproject.toml ./
COPY README.md ./

CMD ["python", "-m", "pytest", "tests"]
```

`docker-compose.yml` (repository root):

```yaml
services:
  booking:
    build:
      context: .
      dockerfile: Dockerfile
    image: hotel-booking:latest
```

*Rationale:* the project has no server, so there is nothing to publish: no ports, no
health check, no volumes. The single service builds the image from the root `Dockerfile`
and the image's default command runs the test suite, so `docker compose up` is a
self-contained check of the delivery.

*Alternative considered:* running a REPL or an idle sleep command so the container stays
alive. Rejected: an idle container proves nothing, whereas running the suite gives a
meaningful exit status.

The compose file deliberately avoids `version:` (obsolete in Compose v2) and avoids any
host-path volume, so the container is reproducible from the repository contents alone.

### D10 — Verification of the container files is static

Because the delivery environment has no Docker daemon, the container files are verified
by inspection rather than by execution: the compose file is parsed with a YAML parser to
confirm it is a mapping with a `services` section whose service declares `build`, and
every `COPY <source>` of the Dockerfile is resolved against the repository to confirm the
source exists. The pytest suite never inspects the content of `Dockerfile`,
`docker-compose.yml`, `README.md` or any script.

*Rationale:* the container is a delivery wrapper; its correctness is a property of the
files and the project layout, and it is covered by the static review in `tasks.md` instead
of by behaviour tests.

## Risks / Trade-offs

- **[Rounding of the discount is ambiguous]** — the request rounds the *result* of
  `stay_total`, so the 10% discount is applied to the full-precision subtotal and
  quantized once at the end. → Mitigation: the discount only ever reduces the room
  subtotal, and the spec pins the two observable totals (7-night and 6-night stays) so any
  divergence from the intended arithmetic is caught by the suite.
- **[Friday/Saturday surcharge boundary]** — a stay can be surcharged on its first two
  nights and not on the rest, which surprises readers who think of a "weekend". →
  Mitigation: the rules are documented per night that *starts* on Friday or Saturday, and
  the worked example (2026-01-02 Friday to 2026-01-04) is pinned in the specs.
- **`datetime` vs `date` confusion at the call site]** — `datetime.datetime` is a
  subclass of `datetime.date`, so a naive implementation would silently accept timestamps.
  → Mitigation: the type guard rejects the subclass explicitly and the specs pin
  `TypeError` for that case.
- **`bool` is an `int` in Python** — `guests=True` would otherwise be read as one guest.
  → Mitigation: the guest guard rejects booleans explicitly, and the specs pin the
  `TypeError`.
- **[The module exposes plain constants]** — a consumer could mutate `BASE_RATES` at
  runtime. → Mitigation: acceptable for a single-team internal library; the constants are
  documented as the pricing table in the README.
- **[No Docker daemon in the delivery environment]** — the image build itself is never
  executed here, so a broken `Dockerfile` could reach the team unnoticed. → Mitigation:
  the static review in `tasks.md` (YAML parse + every `COPY` source exists + image base
  image and `CMD` reviewed by eye) catches the realistic failure modes.
- **[Test suite depends on `pytest` being installed in the image]** — the `RUN pip
  install --no-cache-dir pytest` step needs network access at build time. → Mitigation:
  the base image is pinned to `python:3.11-slim` and the dependency is a single, explicit
  install step.

## Migration Plan

Not applicable — this is a new project with no existing consumers. Adoption for the
revenue team is: `pip install .` in the environment where their scripts run, then
`from booking import nights, nightly_rate, stay_total`. There is no data to migrate and
no rollback beyond deleting the installed package.

## Open Questions

None. Every open point that could have changed the specs, the approach or the task
breakdown was resolved while writing the specs and this document.
