"""Session 7 - pytest fixtures reference."""

FIXTURE_SCOPES = {
    "function": "Default. Best for pages, contexts, mutable data, and isolation.",
    "class": "Shared setup across related methods.",
    "module": "Read-only data or expensive immutable setup for one file.",
    "session": "Full-run setup such as browser instance or loaded config.",
}

FIXTURE_REVIEW_CHECKLIST = [
    "Does the fixture name describe the state it returns?",
    "Is the scope as narrow as practical?",
    "Does cleanup run after the test?",
    "Is the fixture safe under pytest-xdist?",
    "Does the test still make its setup obvious?",
]


def print_fixture_reference() -> None:
    print("Fixture scopes:")
    for scope, use in FIXTURE_SCOPES.items():
        print(f"  {scope}: {use}")
    print("\nReview checklist:")
    for item in FIXTURE_REVIEW_CHECKLIST:
        print(f"  - {item}")


if __name__ == "__main__":
    print_fixture_reference()
