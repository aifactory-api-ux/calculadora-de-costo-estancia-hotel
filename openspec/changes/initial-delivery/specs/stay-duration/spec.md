# Spec Delta

## Purpose

Defines how the hotel stay library counts the nights of a stay and how it validates the
dates it receives, so that every downstream calculation agrees on the length of a stay.

## ADDED Requirements

### Requirement: Night count between two dates

The library SHALL return, as an integer, the number of nights between `check_in` and
`check_out`, counting each night that starts on a date from `check_in` up to and including
the day before `check_out`.

#### Scenario: Two-night stay

- **WHEN** the night count is computed for `check_in` 2026-01-02 and `check_out` 2026-01-04
- **THEN** the result is `2`

#### Scenario: One-night stay

- **WHEN** the night count is computed for `check_in` 2026-01-05 and `check_out` 2026-01-06
- **THEN** the result is `1`

#### Scenario: Stay spanning a month boundary

- **WHEN** the night count is computed for `check_in` 2026-01-30 and `check_out` 2026-02-02
- **THEN** the result is `3`

### Requirement: Stay dates must be plain dates

The library SHALL raise `TypeError` when `check_in` or `check_out` is not an instance of
`datetime.date`, and SHALL also raise `TypeError` when either argument is an instance of
`datetime.datetime`.

#### Scenario: A date argument is not a date

- **WHEN** the night count is computed with `"2026-01-02"` as `check_in` and 2026-01-04 as `check_out`
- **THEN** a `TypeError` is raised

#### Scenario: A check-out argument is not a date

- **WHEN** the night count is computed with 2026-01-02 as `check_in` and `None` as `check_out`
- **THEN** a `TypeError` is raised

#### Scenario: A date argument is a datetime

- **WHEN** the night count is computed with `datetime.datetime(2026, 1, 2, 10, 30)` as `check_in`
- **THEN** a `TypeError` is raised

#### Scenario: A check-out argument is a datetime

- **WHEN** the night count is computed with 2026-01-02 as `check_in` and `datetime.datetime(2026, 1, 4, 18, 0)` as `check_out`
- **THEN** a `TypeError` is raised

### Requirement: Check-out must be after check-in

The library SHALL raise `ValueError` when `check_out` is not later than `check_in`.

#### Scenario: Same-day check-out

- **WHEN** the night count is computed for `check_in` 2026-01-02 and `check_out` 2026-01-02
- **THEN** a `ValueError` is raised

#### Scenario: Check-out before check-in

- **WHEN** the night count is computed for `check_in` 2026-01-04 and `check_out` 2026-01-02
- **THEN** a `ValueError` is raised

### Requirement: Maximum stay of 30 nights

The library SHALL raise `ValueError` when the stay is longer than 30 nights, and SHALL
accept a stay of exactly 30 nights.

#### Scenario: Stay of exactly 30 nights

- **WHEN** the night count is computed for `check_in` 2026-01-01 and `check_out` 2026-01-31
- **THEN** the result is `30`

#### Scenario: Stay of 31 nights

- **WHEN** the night count is computed for `check_in` 2026-01-01 and `check_out` 2026-02-01
- **THEN** a `ValueError` is raised
