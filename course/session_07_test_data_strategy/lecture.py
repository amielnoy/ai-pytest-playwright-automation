"""Session 7 - test data strategy reference."""

DATA_DECISION_TABLE = {
    "public reusable value": "Store in data/test_data.json.",
    "unique value": "Generate through factory or timestamp placeholder.",
    "precondition state": "Create through API or fixture.",
    "private credential": "Store in ignored secrets file or CI secret.",
}


if __name__ == "__main__":
    for need, decision in DATA_DECISION_TABLE.items():
        print(f"{need}: {decision}")
