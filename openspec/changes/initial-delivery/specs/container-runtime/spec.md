# Spec Delta

## Purpose

Defines how the project is containerized: a `Dockerfile` and a `docker-compose.yml` at the
repository root that build the project and run it, so the library can be built and checked
in the same way for everyone.

## ADDED Requirements

### Requirement: Root Dockerfile and compose file build and run the project

The project SHALL provide a `Dockerfile` and a `docker-compose.yml` at the repository root
that together build the project and run it, and since the project is a library with no
server, the container's default command SHALL execute the project's test suite.

#### Scenario: Dockerfile is located at the repository root

- **WHEN** the repository root is inspected
- **THEN** a file named `Dockerfile` exists at the repository root

#### Scenario: Default command runs the test suite

- **WHEN** the image built from the root `Dockerfile` is started with its default command
- **THEN** it executes the project's test suite instead of starting a server

#### Scenario: Every copied source exists in the repository

- **WHEN** the source of each `COPY` instruction of the root `Dockerfile` is resolved
- **THEN** that source path exists in the repository

#### Scenario: Compose file is located at the repository root

- **WHEN** the repository root is inspected
- **THEN** a file named `docker-compose.yml` exists at the repository root

#### Scenario: Compose file is valid YAML describing a buildable service

- **WHEN** the root `docker-compose.yml` is parsed as YAML
- **THEN** it is a mapping whose `services` section contains at least one service that declares a `build` key

#### Scenario: The compose service builds the root Dockerfile

- **WHEN** the compose file is inspected
- **THEN** the buildable service builds its image from the root `Dockerfile`
