# Proposal

## Why

The hotel's revenue team currently has no shared, trustworthy way to price a stay: night
counts, weekend surcharges, the tourist tax and long-stay discounts are computed ad hoc in
their own scripts, so quoted totals can differ between team members. They need a small,
dependency-free Python library that computes a stay cost deterministically so their scripts
can rely on a single source of truth.

## What Changes

- Add a new Python library module `src/booking.py` that exposes three public functions:
  - `nights(check_in, check_out) -> int`: number of nights between two `datetime.date`
    values, rejecting non-`date` inputs (including `datetime`) with `TypeError`,
    non-positive or longer-than-30-night stays with `ValueError`.
  - `nightly_rate(day, room) -> Decimal`: the rate of the night starting on `day` for room
    type `single` (50.00), `double` (80.00) or `suite` (150.00), with a 25% surcharge on
    Friday and Saturday nights, quantized to 2 decimals with `ROUND_HALF_UP`, and
    `ValueError` for an unknown room.
  - `stay_total(check_in, check_out, room, guests) -> Decimal`: the sum of every night of
    the stay plus a 2.50-per-guest-per-night tourist tax, with a 10% discount applied only
    to the room subtotal when the stay is 7 nights or longer, quantized to 2 decimals with
    `ROUND_HALF_UP`; `guests` must be a real `int` between 1 and the room capacity
    (single 1, double 2, suite 4).
- Add a pytest suite covering the documented behaviors, the given worked example and the
  validation boundaries.
- Add a brief README documenting the public API of the library.
- Add a `Dockerfile` and a root `docker-compose.yml` so the project can be built and run
  (the container executes the test suite, since the project is a library with no server).

## Capabilities

### New Capabilities

- `stay-duration`: Number of nights in a stay and the validation of the stay dates
  (types, ordering and the 30-night maximum).
- `room-nightly-pricing`: Per-night room rate for a given room type, the Friday/Saturday
  25% surcharge, rounding rules and rejection of unknown room types.
- `stay-total-quote`: Total cost of a stay: per-night room subtotal, tourist tax, the
  7-night discount and guest-count validation against room capacity.
- `container-runtime`: Containerized build and run of the project via a root `Dockerfile`
  and a root `docker-compose.yml`.

### Modified Capabilities

None. The project has no existing specs; this is the first delivery.

## Impact

- New code: `src/booking.py`, `tests/test_booking.py`.
- New packaging/delivery files: `Dockerfile`, `docker-compose.yml` at the repository root,
  plus a brief `README.md`.
- Dependencies: Python standard library only for the library itself (`datetime`, `decimal`);
  `pytest` is required only to run the test suite.
- Public API surface: the three functions above, imported by the revenue team's scripts.
- No server, no database, no user interface, no network exposure: the project stays a
  library consumed as a dependency.
- The team executing this change is a single Developer agent, which also writes the tests.
