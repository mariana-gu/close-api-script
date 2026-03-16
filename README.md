# close-api-script
# Close CRM Lead Import and Segmentation Script

This project imports company and contact data from a CSV file into Close CRM using the Close API.  
After importing the data, the script finds leads founded within a specified date range and generates a report segmented by US state.

---

## What the Script Does

The script performs three main tasks:

1. Import companies and contacts
2. Find leads within a founded date range
3. Generate a report segmented by state

Each row in the CSV represents a contact.  
Contacts that share the same company name are grouped together into a single Lead in Close CRM.

---

## Handling Invalid Data

The script removes invalid rows before importing them.

Invalid rows include:
- Missing company name
- Invalid revenue values
- Missing required fields

Rows that fail validation are skipped to prevent bad data from entering the CRM.

---

## Creating Leads and Contacts

The script groups rows by company name.

For each company:
- A Lead is created in Close
- Contacts associated with that company are created and attached to the Lead

This ensures that one company can contain multiple contacts.

---

## Finding Leads in a Founded Date Range

After importing data, the script filters leads using the founded date.

Users specify a start date and end date when running the script.

Example:
