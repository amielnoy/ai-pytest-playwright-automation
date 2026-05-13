"""Session 22 - automation code review."""

REVIEW_AREAS = [
    "behavior",
    "layering",
    "locators",
    "data",
    "fixtures",
    "assertions",
    "reports",
]


if __name__ == "__main__":
    for area in REVIEW_AREAS:
        print(f"- {area}")
