# Spec Delta

## Purpose

Defines the price of a single night for each room type, including the weekend surcharge,
the rounding of the resulting amount and the rejection of unknown room types.

## ADDED Requirements

### Requirement: Base rate per room type

The library SHALL return the base rate of a night as a decimal monetary amount, where the
`single` room costs `50.00` per night, the `double` room costs `80.00` per night and the
`suite` room costs `150.00` per night.

#### Scenario: Single room

- **WHEN** the rate is computed for the night starting 2026-01-05 in a `single` room
- **THEN** the result is `50.00`

#### Scenario: Double room

- **WHEN** the rate is computed for the night starting 2026-01-05 in a `double` room
- **THEN** the result is `80.00`

#### Scenario: Suite room

- **WHEN** the rate is computed for the night starting 2026-01-05 in a `suite` room
- **THEN** the result is `150.00`

### Requirement: Friday and Saturday nights carry a 25% surcharge

The library SHALL add a 25% surcharge to the base rate when the night starts on a Friday
or on a Saturday, and SHALL NOT add any surcharge on the other days of the week.

#### Scenario: Night starting on a Friday

- **WHEN** the rate is computed for the night starting 2026-01-02 (a Friday) in a `double` room
- **THEN** the result is `100.00`

#### Scenario: Night starting on a Saturday

- **WHEN** the rate is computed for the night starting 2026-01-03 (a Saturday) in a `single` room
- **THEN** the result is `62.50`

#### Scenario: Night starting on a Sunday

- **WHEN** the rate is computed for the night starting 2026-01-04 (a Sunday) in a `suite` room
- **THEN** the result is `150.00`

#### Scenario: Night starting on a Monday

- **WHEN** the rate is computed for the night starting 2026-01-05 (a Monday) in a `double` room
- **THEN** the result is `80.00`

### Requirement: Rate is rounded to two decimal places

The library SHALL round the rate of a night to 2 decimal places using
`ROUND_HALF_UP`, and SHALL return it as a monetary decimal with exactly 2 decimal places.

#### Scenario: Surcharged suite night

- **WHEN** the rate is computed for the night starting 2026-01-02 (a Friday) in a `suite` room
- **THEN** the result is `187.50`

#### Scenario: Result carries exactly two decimal places

- **WHEN** the rate is computed for the night starting 2026-01-05 in a `double` room
- **THEN** the result is `80.00`, a monetary decimal with exactly 2 decimal places

### Requirement: Unknown room types are rejected

The library SHALL raise `ValueError` when the requested room type is not one of `single`,
`double` or `suite`.

#### Scenario: Unknown room name

- **WHEN** the rate is computed for the night starting 2026-01-05 in a `deluxe` room
- **THEN** a `ValueError` is raised

#### Scenario: Empty room name

- **WHEN** the rate is computed for the night starting 2026-01-05 in a room named `""`
- **THEN** a `ValueError` is raised
