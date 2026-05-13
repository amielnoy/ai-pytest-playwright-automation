# Session 6 - Exercises

## Exercise 1: Exception Audit

Find two places in the framework where an error could happen. Classify each one as configuration, test data, external dependency, assertion, or programmer error.

## Exercise 2: Replace Broad Handling

Write a small function that parses a product price. Catch only `ValueError` and raise a framework exception with useful context.

## Exercise 3: Preserve The Cause

Create a failing example that raises one exception from another. Verify that pytest shows both the framework message and the original cause.

## Exercise 4: Retry A Transient Error

Write a function that fails once with `TimeoutError` and then succeeds. Use the framework retry helper to retry only that exception type.

## Exercise 5: Review Failure Quality

Run a failing test and write a short review note: is the failure actionable, does it preserve the root cause, and does it avoid hiding a product bug?
