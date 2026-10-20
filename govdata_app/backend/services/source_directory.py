import os
import json
import pandas as pd
from typing import List, Dict, Any

DIRECTORY = [
    {
        "id": "nso-nepal",
        "name": "National Statistics Office (NSO) Nepal",
        "url": "https://nsonepal.gov.np/",
        "category": "Demographics & National Census",
        "country": "Nepal",
        "is_official": True,
        "description": "Apex statistical agency of the Government of Nepal producing Census, Economic, and Living Standards reports.",
        "sample_dataset_file": "nepal_census_2021_summary.csv",
        "available_endpoints": [
            "https://nsonepal.gov.np/publications",
            "https://nsonepal.gov.np/census-data"
        ]
    },
    {
        "id": "open-data-nepal",
        "name": "Open Data Nepal (Open Knowledge Nepal)",
        "url": "https://opendatanepal.com/",
        "category": "Open Data Portal & Civil Society",
        "country": "Nepal",
        "is_official": False,
        "description": "Comprehensive civil data portal with open datasets across Nepal's infrastructure, budget, and education.",
        "sample_dataset_file": "nepal_foreign_trade_statistics.csv",
        "available_endpoints": [
            "https://opendatanepal.com/dataset",
            "https://opendatanepal.com/api/3/action/package_search"
        ]
    },
    {
        "id": "election-commission",
        "name": "Election Commission Nepal",
        "url": "https://election.gov.np/",
        "category": "Governance & Elections",
        "country": "Nepal",
        "is_official": True,
        "description": "Official constitutional body conducting local, provincial, and parliamentary elections across Nepal.",
        "sample_dataset_file": "nepal_voter_turnout_by_province.csv",
        "available_endpoints": [
            "https://election.gov.np/np/results"
        ]
    },
    {
        "id": "nrb-central-bank",
        "name": "Nepal Rastra Bank (Central Bank of Nepal)",
        "url": "https://www.nrb.org.np/",
        "category": "Macroeconomics & Banking",
        "country": "Nepal",
        "is_official": True,
        "description": "Monetary policy, foreign exchange rates, inflation indices, and commercial banking indicators.",
        "sample_dataset_file": "nepal_inflation_macroeconomic_indicators.csv",
        "available_endpoints": [
            "https://www.nrb.org.np/api/forex/v1/rates"
        ]
    },
    {
        "id": "mof-nepal",
        "name": "Ministry of Finance - Nepal",
        "url": "https://mof.gov.np/",
        "category": "Public Finance & Budget",
        "country": "Nepal",
        "is_official": True,
        "description": "National budget statements, economic surveys, and revenue mobilization statistics.",
        "sample_dataset_file": "nepal_provincial_budget_allocation.csv",
        "available_endpoints": [
            "https://mof.gov.np/economic-survey"
        ]
    },
    {
        "id": "data-gov-us",
        "name": "Data.gov (United States Government)",
        "url": "https://data.gov/",
        "category": "International Open Data",
        "country": "United States",
        "is_official": True,
        "description": "The home of the U.S. Government’s open data, offering metadata and APIs across hundreds of thousands of public datasets.",
        "available_endpoints": [
            "https://catalog.data.gov/api/3/action/package_search"
        ]
    }
]

def get_directory() -> List[Dict[str, Any]]:
    return DIRECTORY

def generate_sample_datasets(samples_dir: str):
    """
    Creates realistic, structured reference datasets representing public government publications
    for instant verification, testing, and offline analytical exploration.
    """
    os.makedirs(samples_dir, exist_ok=True)

    # 1. Nepal 2021 Census Provincial Summary
    census_path = os.path.join(samples_dir, "nepal_census_2021_summary.csv")
    if not os.path.exists(census_path):
        census_data = {
            "Province": ["Koshi", "Madhesh", "Bagmati", "Gandaki", "Lumbini", "Karnali", "Sudurpashchim"],
            "Capital": ["Biratnagar", "Janakpur", "Hetauda", "Pokhara", "Deukhuri", "Birendranagar", "Godawari"],
            "Districts_Count": [14, 8, 13, 11, 12, 10, 9],
            "Total_Population": [4961412, 6114600, 6116866, 2466427, 5122078, 1688412, 2694783],
            "Male_Population": [2417328, 3065669, 3048596, 1170833, 2454594, 823761, 1272786],
            "Female_Population": [2544084, 3048931, 3068270, 1295594, 2667484, 864651, 1421997],
            "Sex_Ratio": [95.02, 100.55, 99.36, 90.37, 92.02, 95.27, 89.51],
            "Annual_Growth_Rate_Pct": [0.86, 1.19, 0.97, 0.25, 1.24, 0.70, 0.52],
            "Literacy_Rate_Pct": [79.7, 63.5, 82.1, 81.7, 78.1, 76.1, 76.2],
            "Area_SqKm": [25905, 9661, 20300, 21504, 22288, 27984, 19539]
        }
        pd.DataFrame(census_data).to_csv(census_path, index=False)

    # 2. Nepal Foreign Trade Statistics (Customs / Trade Portal)
    trade_path = os.path.join(samples_dir, "nepal_foreign_trade_statistics.csv")
    if not os.path.exists(trade_path):
        trade_data = {
            "Fiscal_Year": ["2075/76", "2076/77", "2077/78", "2078/79", "2079/80", "2080/81"],
            "Imports_NPR_Billion": [1418.5, 1196.8, 1539.8, 1920.4, 1611.7, 1592.9],
            "Exports_NPR_Billion": [97.1, 97.7, 141.1, 200.0, 157.1, 152.4],
            "Trade_Deficit_NPR_Billion": [1321.4, 1099.1, 1398.7, 1720.4, 1454.6, 1440.5],
            "Export_Import_Ratio": [0.068, 0.082, 0.092, 0.104, 0.097, 0.096],
            "Primary_Partner": ["India", "India", "India", "India", "India", "India"]
        }
        pd.DataFrame(trade_data).to_csv(trade_path, index=False)

    # 3. Election Commission Voter Turnout by Province
    election_path = os.path.join(samples_dir, "nepal_voter_turnout_by_province.csv")
    if not os.path.exists(election_path):
        election_data = {
            "Province": ["Koshi", "Madhesh", "Bagmati", "Gandaki", "Lumbini", "Karnali", "Sudurpashchim"],
            "Registered_Voters": [3396865, 3386628, 3471492, 1817342, 3249637, 1008403, 1658402],
            "Votes_Cast": [2231743, 2218247, 2155796, 1184907, 2199979, 655462, 1079620],
            "Turnout_Percentage": [65.7, 65.5, 62.1, 65.2, 67.7, 65.0, 65.1],
            "Valid_Votes": [2113490, 2085152, 2041538, 1129216, 2074579, 616134, 1018081],
            "Invalid_Votes": [118253, 133095, 114258, 55691, 125400, 39328, 61539]
        }
        pd.DataFrame(election_data).to_csv(election_path, index=False)

    # 4. Nepal Rastra Bank Macroeconomic & Inflation
    nrb_path = os.path.join(samples_dir, "nepal_inflation_macroeconomic_indicators.csv")
    if not os.path.exists(nrb_path):
        nrb_data = {
            "Month": ["Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra", "Baisakh", "Jestha", "Ashadh"],
            "Inflation_Rate_Pct": [7.52, 8.19, 8.50, 8.08, 7.38, 7.26, 7.88, 7.44, 7.76, 7.41, 6.83, 5.75],
            "Food_Beverage_Inflation": [6.94, 7.61, 8.05, 7.38, 5.85, 5.62, 5.91, 5.64, 6.93, 7.02, 6.72, 5.80],
            "Non_Food_Inflation": [7.98, 8.67, 8.85, 8.63, 8.59, 8.57, 9.43, 8.87, 8.42, 7.72, 6.92, 5.71],
            "Remittance_Inflow_NPR_Billion": [92.7, 94.3, 94.0, 97.2, 102.5, 104.1, 104.8, 103.2, 109.1, 102.3, 105.4, 114.7],
            "Foreign_Exchange_Reserves_USD_Billion": [9.42, 9.35, 9.48, 9.63, 9.82, 10.30, 10.50, 10.69, 10.94, 11.20, 11.71, 11.71]
        }
        pd.DataFrame(nrb_data).to_csv(nrb_path, index=False)

    # 5. Ministry of Finance Provincial Budget Allocation
    mof_path = os.path.join(samples_dir, "nepal_provincial_budget_allocation.csv")
    if not os.path.exists(mof_path):
        mof_data = {
            "Province": ["Koshi", "Madhesh", "Bagmati", "Gandaki", "Lumbini", "Karnali", "Sudurpashchim"],
            "Equalization_Grant_NPR_Crore": [874, 769, 804, 762, 843, 1016, 887],
            "Conditional_Grant_NPR_Crore": [938, 1124, 1102, 680, 894, 634, 712],
            "Special_Grant_NPR_Crore": [125, 94, 142, 98, 118, 160, 134],
            "Complementary_Grant_NPR_Crore": [112, 85, 120, 89, 105, 140, 115],
            "Total_Federal_Transfer_NPR_Crore": [2049, 2072, 2168, 1629, 1960, 1950, 1848]
        }
        pd.DataFrame(mof_data).to_csv(mof_path, index=False)
