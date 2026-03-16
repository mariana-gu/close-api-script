import csv
import requests
import statistics
import argparse
from collections import defaultdict

# -----------------------------
# CONFIGURATION
# -----------------------------
API_KEY = "api_5DLQVzkKZ5PbjPcg1M66zw.7m84VtzTABLXYxXLpxZPP2"
BASE_URL = "https://api.close.com/api/v1"

HEADERS = {
    "Content-Type": "application/json"
}

# -----------------------------
# FUNCTION: READ CSV AND CLEAN DATA
# -----------------------------
def read_csv(file_path):
    """
    Reads CSV and removes invalid rows.
    Invalid data includes rows missing company name,
    contact name, state, or revenue.
    """
    valid_rows = []

    with open(file_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if not row.get("company_name"):
                continue

            try:
                revenue = float(row.get("revenue", 0))
            except ValueError:
                continue

            row["revenue"] = revenue
            valid_rows.append(row)

    return valid_rows


# -----------------------------
# FUNCTION: GROUP CONTACTS BY COMPANY
# -----------------------------
def group_by_company(rows):
    """
    Groups CSV contacts by company name.
    Each company becomes one Lead.
    """
    companies = defaultdict(list)

    for row in rows:
        companies[row["company_name"]].append(row)

    return companies


# -----------------------------
# FUNCTION: CREATE LEADS IN CLOSE
# -----------------------------
def create_leads(companies):
    """
    Creates leads in Close and attaches contacts.
    """
    created_leads = []

    for company, contacts in companies.items():

        lead_payload = {
            "name": company
        }

        r = requests.post(
            f"{BASE_URL}/lead/",
            auth=(API_KEY, ""),
            json=lead_payload
        )

        lead = r.json()
        lead_id = lead["id"]

        created_leads.append(lead)

        # create contacts for lead
        for c in contacts:

            contact_payload = {
                "lead_id": lead_id,
                "name": c.get("contact_name"),
                "emails": [{"email": c.get("email")}],
            }

            requests.post(
                f"{BASE_URL}/contact/",
                auth=(API_KEY, ""),
                json=contact_payload
            )

    return created_leads


# -----------------------------
# FUNCTION: FILTER LEADS BY FOUNDED DATE
# -----------------------------
def filter_leads_by_founded(leads, start, end):
    """
    Returns leads founded within a given range.
    """

    filtered = []

    for lead in leads:

        founded = lead.get("founded")

        if not founded:
            continue

        if start <= founded <= end:
            filtered.append(lead)

    return filtered


# -----------------------------
# FUNCTION: SEGMENT BY STATE
# -----------------------------
def segment_by_state(leads):
    """
    Groups leads by state and calculates revenue metrics.
    """

    states = defaultdict(list)

    for lead in leads:
        state = lead.get("state")
        revenue = lead.get("revenue", 0)

        if state:
            states[state].append(revenue)

    results = []

    for state, revenues in states.items():

        total_revenue = sum(revenues)
        median_revenue = statistics.median(revenues)
        lead_count = len(revenues)
        max_revenue = max(revenues)

        results.append({
            "state": state,
            "lead_count": lead_count,
            "max_revenue": max_revenue,
            "total_revenue": total_revenue,
            "median_revenue": median_revenue
        })

    return results


# -----------------------------
# FUNCTION: EXPORT CSV
# -----------------------------
def export_csv(results, filename="state_report.csv"):

    with open(filename, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "State",
            "Total Leads",
            "Lead With Most Revenue",
            "Total Revenue",
            "Median Revenue"
        ])

        for r in results:
            writer.writerow([
                r["state"],
                r["lead_count"],
                r["max_revenue"],
                r["total_revenue"],
                r["median_revenue"]
            ])


# -----------------------------
# MAIN SCRIPT
# -----------------------------
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--start")
    parser.add_argument("--end")

    args = parser.parse_args()

    rows = read_csv(args.csv)

    companies = group_by_company(rows)

    leads = create_leads(companies)

    filtered = filter_leads_by_founded(
        leads,
        args.start,
        args.end
    )

    results = segment_by_state(filtered)

    export_csv(results)


if __name__ == "__main__":
    main()
