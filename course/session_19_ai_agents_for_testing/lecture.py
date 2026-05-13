"""
Session 19 - AI Agents for Testing
Key concepts: input contracts, risk inventories, review gates, framework mapping.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentInputContract:
    feature: str
    requirement: str
    risks: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    output_format: tuple[str, ...]


@dataclass(frozen=True)
class AgentFinding:
    finding: str
    risk: str
    framework_action: str
    review_status: str


SEARCH_CONTRACT = AgentInputContract(
    feature="Search under maximum price",
    requirement="Users can search for products and verify displayed prices are within a chosen budget.",
    risks=(
        "Price text may include tax or currency formatting.",
        "Search results may include unrelated products.",
        "Empty result states may be missed.",
    ),
    out_of_scope=(
        "Real payment behavior",
        "Third-party analytics",
    ),
    output_format=(
        "Risk table",
        "Functional tests",
        "Negative tests",
        "Automation candidates",
        "Open questions",
    ),
)


SAMPLE_FINDINGS = [
    AgentFinding(
        finding="Verify every visible product price is less than or equal to the configured maximum.",
        risk="Incorrect price parsing can allow products above budget.",
        framework_action="Add assertion through SearchResultsPage and price_parser utility.",
        review_status="accept",
    ),
    AgentFinding(
        finding="Verify payment is processed after search.",
        risk="Not related to search results.",
        framework_action="Reject as out of scope for this feature.",
        review_status="reject",
    ),
    AgentFinding(
        finding="Check empty search results for a clear message.",
        risk="Users need feedback when no product matches.",
        framework_action="Add or update SearchResultsPage empty-state method.",
        review_status="revise",
    ),
]


def print_contract(contract: AgentInputContract) -> None:
    print(f"Feature: {contract.feature}")
    print(f"Requirement: {contract.requirement}")
    print("\nRisks:")
    for risk in contract.risks:
        print(f"  - {risk}")
    print("\nOut of scope:")
    for item in contract.out_of_scope:
        print(f"  - {item}")
    print("\nRequired output:")
    for item in contract.output_format:
        print(f"  - {item}")


def print_review(findings: list[AgentFinding]) -> None:
    print("\nAgent finding review:")
    for finding in findings:
        print(f"  [{finding.review_status}] {finding.finding}")
        print(f"      Risk: {finding.risk}")
        print(f"      Action: {finding.framework_action}")


if __name__ == "__main__":
    print_contract(SEARCH_CONTRACT)
    print_review(SAMPLE_FINDINGS)
