# Session 7 - Exercises

## Exercise 1: Fixture Scope Audit

Review `conftest.py` and classify each fixture by scope and responsibility. For each fixture, explain whether the scope is appropriate.

## Exercise 2: Create a `yield` Fixture

Create a fixture that prepares temporary data and cleans it up after the test. If real cleanup is not possible, write a simulated cleanup step and explain what production cleanup would do.

## Exercise 3: Remove Hidden Setup

Find a test with repeated setup steps. Extract the setup into an explicit fixture whose name describes the state it creates.

## Exercise 4: Parametrized Fixture

Create a parametrized fixture with two user roles or two search terms. Use it in one focused test.

## Exercise 5: Fixture Review

Write a review note for one fixture: what it creates, who owns cleanup, whether it is parallel-safe, and what could make it flaky.
