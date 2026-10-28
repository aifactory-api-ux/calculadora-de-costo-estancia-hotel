# Spec Delta

## Purpose

Defines the total cost of a stay: the sum of the rates of every night, the tourist tax
charged per guest and per night, the discount granted on long stays and the validation of
the guest count against the capacity of the room.

## ADDED Requirements

### Requirement: Total combines every night of the stay with the tourist tax

The library SHALL return, as a decimal monetary amount, the sum of the rate of every night
of the stay — from `check_in` up to the day before `check_out` — plus a tourist tax of
`2.50` per guest for each night of the stay.

#### Scenario: Worked example of a two-night weekend stay

- **WHEN** the total is computed for `check_in` 2026-01-02 (a Friday), `check_out` 2026-01-04, a `double` room and `2` guests
- **THEN** the result is `210.00`, made up of `100.00` for the Friday night, `100.00` for the Saturday night and `10.00` of tourist tax

#### Scenario: Tourist tax scales with guests and nights

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `single` room and `1` guest
- **THEN** the result is `52.50`, made up of `50.00` for the room and `2.50` of tourist tax

### Requirement: Guest count must be an integer

The library SHALL raise `TypeError` when the guest count is not an integer, and SHALL also
raise `TypeError` when the guest count is a boolean.

#### Scenario: Fractional guest count

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `double` room and `2.5` guests
- **THEN** a `TypeError` is raised

#### Scenario: Boolean guest count

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `double` room and `True` guests
- **THEN** a `TypeError` is raised

### Requirement: Guest count must fit the capacity of the room

The library SHALL raise `ValueError` when the guest count is lower than `1` or higher than
the capacity of the room, where the capacity is `1` for a `single` room, `2` for a `double`
room and `4` for a `suite` room.

#### Scenario: More guests than the room holds

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `single` room and `2` guests
- **THEN** a `ValueError` is raised

#### Scenario: No guests

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `double` room and `0` guests
- **THEN** a `ValueError` is raised

#### Scenario: Guest count equal to the capacity

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `suite` room and `4` guests
- **THEN** the result is `160.00`, made up of `150.00` for the room and `10.00` of tourist tax

### Requirement: Stays of 7 nights or more get a 10% discount on the room subtotal

The library SHALL apply a 10% discount to the room subtotal when the stay lasts 7 nights
or more, SHALL NOT apply that discount when the stay lasts 6 nights or fewer, and SHALL
NEVER apply the discount to the tourist tax.

#### Scenario: Seven-night stay is discounted

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-12, a `double` room and `2` guests
- **THEN** the result is `575.00`, made up of a discounted room subtotal of `540.00` and a tourist tax of `35.00`

#### Scenario: Six-night stay is not discounted

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-11, a `double` room and `2` guests
- **THEN** the result is `550.00`, made up of a room subtotal of `520.00` and a tourist tax of `30.00`

#### Scenario: Discount leaves the tourist tax untouched

- **WHEN** the total is computed for a stay of 7 nights in a `double` room with `2` guests
- **THEN** the tourist tax charged is `35.00`, being `2.50` per guest for each of the 7 nights

### Requirement: Unknown room types are rejected

The library SHALL raise `ValueError` when the requested room type is not one of `single`,
`double` or `suite`.

#### Scenario: Unknown room name

- **WHEN** the total is computed for `check_in` 2026-01-05, `check_out` 2026-01-06, a `deluxe` room and `2` guests
- **THEN** a `ValueError` is raised

### Requirement: Stay dates are validated

The library SHALL apply the same date validation as the night count when computing a
total: a `TypeError` for arguments that are not plain `datetime.date` values (including
`datetime.datetime` values), and a `ValueError` when `check_out` is not later than
`check_in` or when the stay is longer than 30 nights.

#### Scenario: Check-out on the same day as check-in

- **WHEN** the total is computed for `check_in` 2026-01-02, `check_out` 2026-01-02, a `double` room and `2` guests
- **THEN** a `ValueError` is raised

#### Scenario: Stay longer than 30 nights

- **WHEN** the total is computed for `check_in` 2026-01-01, `check_out` 2026-02-01, a `double` room and `2` guests
- **THEN** a `ValueError` is raised

#### Scenario: A date argument is a datetime

- **WHEN** the total is computed with `datetime.datetime(2026, 1, 2, 10, 30)` as `check_in`
- **THEN** a `TypeError` is raised

### Requirement: Total is rounded to two decimal places

The library SHALL round the total of a stay to 2 decimal places using `ROUND_HALF_UP`, and
SHALL return it as a monetary decimal with exactly 2 decimal places.

#### Scenario: Result carries exactly two decimal places

- **WHEN** the total is computed for `check_in` 2026-01-02, `check_out` 2026-01-04, a `double` room and `2` guests
- **THEN** the result is `210.00`, a monetary decimal with exactly 2 decimal places
