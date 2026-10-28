# Tasks

Implementation checklist for `initial-delivery`. All work is executed by the **single
Developer agent** of the team (there is no QA role and no DevSec role); the same Developer
writes the tests of every group. Reference `specs/` for the behaviour to build and
`design.md` for the approach.

Files to create (exact paths): `src/booking.py`, `tests/test_booking.py`, `pyproject.toml`,
`README.md`, `Dockerfile`, `docker-compose.yml`.

## 1. Night counting and stay-date validation

- [x] 1.1 Create `src/booking.py` and implement `nights(check_in, check_out) -> int` returning the number of nights between two dates, counting each night that starts on a date from `check_in` up to the day before `check_out`; verify with `PYTHONPATH=src python -c "from booking import nights; from datetime import date; print(nights(date(2026,1,2), date(2026,1,4)))"` printing `2`.
- [x] 1.2 Add the date type guard so that an argument that is not a `datetime.date` instance — including a `datetime.datetime` instance, which is a subclass of `date` — raises `TypeError`, and make the guard run before any date comparison; verify with `PYTHONPATH=src python -c "from booking import nights; from datetime import datetime, date; nights(datetime(2026,1,2,10,30), date(2026,1,4))"` raising `TypeError`.
- [x] 1.3 Make `nights` raise `ValueError` when `check_out` is not later than `check_in` and when the stay exceeds the 30-night maximum, while accepting exactly 30 nights; verify with `PYTHONPATH=src python -c "from booking import nights; from datetime import date; nights(date(2026,1,1), date(2026,1,31))"` printing `30` and `nights(date(2026,1,1), date(2026,2,1))` raising `ValueError`.
- [x] 1.4 Add to `tests/test_booking.py` the tests for this group — night counts (one night, two nights, a stay spanning a month boundary), `TypeError` for a non-date argument and for a `datetime` argument on either side, `ValueError` for a same-day check-out and for a reversed check-out, and the 30-night boundary (30 accepted, 31 rejected); verify `python -m pytest tests/test_booking.py` passes.

## 2. Nightly rate per room type

- [x] 2.1 In `src/booking.py`, define the base rate constants (`single` 50.00, `double` 80.00, `suite` 150.00) as `Decimal` values built from string literals, and implement `nightly_rate(day, room) -> Decimal` returning the base rate of the night that starts on `day`; verify with `PYTHONPATH=src python -c "from booking import nightly_rate; from datetime import date; print(nightly_rate(date(2026,1,5), 'double'))"` printing `80.00`.
- [x] 2.2 Apply the 25% surcharge to the nights that start on a Friday or a Saturday and no surcharge on the other days, and quantize the result to 2 decimal places with `ROUND_HALF_UP`; verify with `PYTHONPATH=src python -c "from booking import nightly_rate; from datetime import date; print(nightly_rate(date(2026,1,2), 'double'), nightly_rate(date(2026,1,3), 'single'), nightly_rate(date(2026,1,4), 'suite'))"` printing `100.00 62.50 150.00`.
- [x] 2.3 Make `nightly_rate` raise `ValueError` when the room type is not one of `single`, `double` or `suite`; verify with `PYTHONPATH=src python -c "from booking import nightly_rate; from datetime import date; nightly_rate(date(2026,1,5), 'deluxe')"` raising `ValueError`.
- [x] 2.4 Add to `tests/test_booking.py` the tests for this group — one per base rate, the Friday and the Saturday surcharge, a non-surcharged Sunday and Monday, the two-decimal formatting of the result and the unknown-room failure; verify `python -m pytest tests/test_booking.py` passes.

## 3. Total cost of a stay

- [x] 3.1 Implement `stay_total(check_in, check_out, room, guests) -> Decimal` in `src/booking.py` as the sum of `nightly_rate` for every night of the stay (from `check_in` up to the day before `check_out`), validating the dates through `nights` so an invalid range raises `ValueError` and a non-`date` argument raises `TypeError`; verify with `PYTHONPATH=src python -c "from booking import stay_total; from datetime import date; print(stay_total(date(2026,1,5), date(2026,1,6), 'single', 1))"` printing `52.50`.
- [x] 3.2 Add the tourist tax of 2.50 per guest for each night of the stay on top of the room subtotal; verify with the same command as 3.1, where the `52.50` result is `50.00` of room plus `2.50` of tax for one guest and one night.
- [x] 3.3 Apply a 10% discount to the room subtotal only — never to the tourist tax — when the stay lasts 7 nights or more, and apply no discount for 6 nights or fewer; verify with `PYTHONPATH=src python -c "from booking import stay_total; from datetime import date; print(stay_total(date(2026,1,5), date(2026,1,12), 'double', 2), stay_total(date(2026,1,5), date(2026,1,11), 'double', 2))"` printing `575.00 550.00`.
- [x] 3.4 Validate the guest count: raise `TypeError` when it is not an `int` (a `bool` included) and `ValueError` when it is below 1 or above the capacity of the room (`single` 1, `double` 2, `suite` 4), and raise `ValueError` for an unknown room type; verify with `PYTHONPATH=src python -c "from booking import stay_total; from datetime import date; stay_total(date(2026,1,5), date(2026,1,6), 'double', True)"` raising `TypeError` and `stay_total(date(2026,1,5), date(2026,1,6), 'single', 2)` raising `ValueError`.
- [x] 3.5 Quantize the final total to 2 decimal places with `ROUND_HALF_UP`; verify with `PYTHONPATH=src python -c "from booking import stay_total; from datetime import date; t = stay_total(date(2026,1,2), date(2026,1,4), 'double', 2); print(t, t.as_tuple().exponent)"` printing `210.00 -2`.
- [x] 3.6 Add to `tests/test_booking.py` the tests for this group — the worked example (2026-01-02 Friday to 2026-01-04, `double`, 2 guests) returning `210.00`, the tax scaling with guests and nights, the 7-night discounted total `575.00`, the 6-night undiscounted total `550.00`, the discount leaving the tax untouched, the guest-count type failures (fractional and boolean), the guest-count range failures (zero guests, guests above the capacity), a guest count equal to the capacity, the unknown-room failure, the invalid date range failures and the two-decimal formatting of the result; verify `python -m pytest tests/test_booking.py` passes.

## 4. Packaging and README

- [x] 4.1 Add `pyproject.toml` declaring the project with setuptools in a src layout (`package-dir = {"" = "src"}`, `py-modules = ["booking"]`, `requires-python >= 3.9`) and the pytest configuration (`pythonpath = ["src"]`, `testpaths = ["tests"]`); verify that `python -m pytest` collects and passes from the repository root without installing the package.
- [x] 4.2 Write the brief `README.md`: what the library is for, how to install it as a dependency (`pip install .`) and import it (`from booking import nights, nightly_rate, stay_total`), the signature and the error semantics of each of the three functions, the rates and capacities table, the worked example with its `210.00` result and the `pytest` command to run the suite; verify that the example result printed in the README matches the value returned by `stay_total(date(2026,1,2), date(2026,1,4), 'double', 2)`.

## 5. Containerization

- [x] 5.1 Add the root `Dockerfile`: base image `python:3.11-slim`, `WORKDIR /app`, `pip install --no-cache-dir pytest`, `COPY` of `src/`, `tests/`, `pyproject.toml` and `README.md`, and `CMD ["python", "-m", "pytest", "tests"]` as the default command, since the project is a library with no server; verify statically that every `COPY` source exists in the repository (no `docker build` is run in this environment).
- [x] 5.2 Add the root `docker-compose.yml` with a single service `booking` that declares `build` with `context: .` and `dockerfile: Dockerfile`, and no ports or volumes; verify statically by parsing the file with a YAML parser that it is a mapping whose `services` section holds that buildable service (no `docker compose up` is run in this environment).
- [x] 5.3 Review both container files against the repository layout: confirm the image copies the module and its tests, that the default command runs the test suite instead of starting a server, and that no command in this group requires a Docker daemon.

## 6. Final verification

- [x] 6.1 Run the complete suite from the repository root with `python -m pytest` and confirm every test of `tests/test_booking.py` passes.
- [x] 6.2 Confirm the public API surface: `nights`, `nightly_rate` and `stay_total` are importable from `booking`, and the worked example returns `Decimal("210.00")`.
- [x] 6.3 Confirm the repository holds only the agreed deliverables — `src/booking.py`, `tests/test_booking.py`, `pyproject.toml`, `README.md`, `Dockerfile`, `docker-compose.yml` — plus the OpenSpec workspace, with no leftover scratch files.

## Workflow follow-up

- Archive the change with `openspec archive initial-delivery` once the delivery is reviewed.
- Verify the archived result: `openspec validate --strict` still passes and the archived spec files match the delivered behaviour.
