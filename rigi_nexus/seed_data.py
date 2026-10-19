"""
KMC-HSSD Seed Data & Complete Demonstration Workflows
All demonstration records are explicitly labeled with [SAMPLE / DEMO].
Provides initial researchers, research ideas, proposals, projects, datasets,
scientific experiments, peer-reviewed references, funding grants, ethics reviews,
and SDG impact observatory indicators.
"""

import sqlite3
import json
import os
import hashlib
from database import DB_PATH

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing sample data if any to ensure clean idempotent state
    cur.execute("DELETE FROM audit_logs")
    cur.execute("DELETE FROM notifications")
    cur.execute("DELETE FROM impact_indicators")
    cur.execute("DELETE FROM ethics_records")
    cur.execute("DELETE FROM collaborations")
    cur.execute("DELETE FROM funding_opportunities")
    cur.execute("DELETE FROM learning_resources")
    cur.execute("DELETE FROM publications")
    cur.execute("DELETE FROM experiments")
    cur.execute("DELETE FROM analysis_runs")
    cur.execute("DELETE FROM datasets")
    cur.execute("DELETE FROM milestones")
    cur.execute("DELETE FROM tasks")
    cur.execute("DELETE FROM projects")
    cur.execute("DELETE FROM proposals")
    cur.execute("DELETE FROM research_ideas")
    cur.execute("DELETE FROM institutions")
    cur.execute("DELETE FROM researcher_profiles")
    cur.execute("DELETE FROM users")

    # 1. Users
    users_data = [
        ("user_bishnu", "Dr. Bishnu S. Rayamajhi", "bishnu@rigi-nexus.edu", hash_pw("research2026"), "researcher", "Tribhuvan University & KMC-HSSD Global Institute", "👨‍🏫"),
        ("user_elena", "Prof. Elena Rostova", "elena.rostova@cambridge-ri.org", hash_pw("cambridge2026"), "supervisor", "University of Cambridge", "👩‍🔬"),
        ("user_kwame", "Dr. Kwame Mensah", "kwame.mensah@ghana-tech.edu", hash_pw("accra2026"), "reviewer", "Kwame Nkrumah University of Science and Technology", "👨‍💻"),
        ("user_sophia", "Sophia Chen, M.Sc.", "sophia.chen@stanford-ai.org", hash_pw("stanford2026"), "student", "Stanford Artificial Intelligence Lab", "👩‍🎓"),
        ("user_admin", "System Governance Admin", "admin@rigi-nexus.org", hash_pw("adminSecure2026"), "administrator", "KMC-HSSD Global Governance Council", "🛡️")
    ]
    cur.executemany("INSERT INTO users (id, name, email, password_hash, role, institution, avatar) VALUES (?, ?, ?, ?, ?, ?, ?)", users_data)

    # 2. Researcher Profiles
    profiles = [
        ("user_bishnu", "Senior Research Fellow in Computational Sustainability", 
         "Focused on AI-driven ecological modeling, climate resilience in mountainous regions, and open scientific data infrastructure.",
         "0000-0002-1825-0097", "Department of Environmental & Information Systems", "Computational Ecology & Data Science",
         json.dumps(["Climate Modeling", "Machine Learning in Agriculture", "Research Reproducibility", "SDG 13"]), 18, 1420, "https://scholar.rigi-nexus.org/bishnu", "https://scholar.google.com", 1),
        
        ("user_elena", "Chair of Renewable Energy Physics",
         "Pioneering perovskite solar cell stability metrics and international energy democratization policies.",
         "0000-0003-9124-7718", "Cavendish Laboratory", "Renewable Energy & Photovoltaics",
         json.dumps(["Perovskite Solar Cells", "Clean Energy Transition", "Material Informatics", "SDG 7"]), 34, 4890, "https://cambridge.org/elena", "https://scholar.google.com", 1),

        ("user_kwame", "Associate Professor of Public Health Epidemiology",
         "Lead investigator in epidemiological tracking of climate-sensitive vector-borne diseases in Sub-Saharan Africa.",
         "0000-0001-5529-8831", "School of Public Health", "Epidemiology & Biostatistics",
         json.dumps(["Vector-borne Dynamics", "Bayesian Spatial Statistics", "Global Health Equity", "SDG 3"]), 22, 2105, "https://knust.edu.gh/kwame", "https://scholar.google.com", 1),

        ("user_sophia", "PhD Candidate in Trustworthy AI",
         "Researching algorithmic fairness, synthetic data validation, and scientific reproducibility frameworks.",
         "0000-0004-3321-4902", "Stanford AI Lab", "Artificial Intelligence & Ethics",
         json.dumps(["Explainable AI", "Statistical Bias Correction", "Responsible Research", "SDG 9"]), 8, 340, "https://sophiachen.ai", "https://scholar.google.com", 1),
    ]
    cur.executemany("""INSERT INTO researcher_profiles 
        (user_id, title, bio, orcid_id, department, field_of_study, research_interests, h_index, total_citations, website, google_scholar, available_for_collab)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", profiles)

    # 3. Institutions
    institutions = [
        ("inst_tu", "Tribhuvan University", "Nepal", "University", "https://tu.edu.np", 1),
        ("inst_cam", "University of Cambridge", "United Kingdom", "University", "https://cam.ac.uk", 1),
        ("inst_knust", "KNUST College of Health Sciences", "Ghana", "University & Lab", "https://knust.edu.gh", 1),
        ("inst_stanford", "Stanford University", "United States", "University", "https://stanford.edu", 1),
        ("inst_icimod", "ICIMOD (Intl. Centre for Integrated Mountain Development)", "Regional", "Research Institute", "https://icimod.org", 1)
    ]
    cur.executemany("INSERT INTO institutions (id, name, country, type, website, verified) VALUES (?, ?, ?, ?, ?, ?)", institutions)

    # 4. Research Ideas
    ideas = [
        ("idea_climate_agri", "user_bishnu", 
         "[SAMPLE] Microclimate Sensor Networks & Machine Learning for Mountain Smallholder Resilience",
         "Smallholder mountain farmers face severe yield volatility from unpredicted microclimatic shifts. Conventional regional weather forecasts fail to capture steep topographic gradient variations.",
         "Existing agro-climatic forecasting models are trained on coarse 25km satellite grids without localized IoT calibration, creating a 68% inaccuracy in high-altitude valleys.",
         json.dumps(["How do micro-elevation temperature inversions affect frost damage probabilities?", "Can a lightweight Gaussian Process model predict local frost events 48 hours in advance?"]),
         json.dumps(["H1: Edge-deployed micro-stations combined with localized regression will reduce frost prediction error by >35% compared to regional reanalysis data."]),
         "1. Deploy 15 solar-powered IoT micro-nodes across a 1,200m elevation transect. 2. Develop an interpretable predictive model for local agronomists.",
         "Directly impacts food security for over 45,000 mountain households and provides an open hardware/software blueprint.",
         "Socio-Ecological Systems Resilience Theory (Ostrom, 2009) and Boundary-Layer Meteorologic Thermodynamics.",
         json.dumps(["SDG 2: Zero Hunger", "SDG 13: Climate Action", "SDG 1: No Poverty"]),
         "converted_to_proposal", 1),

        ("idea_sir_epidemic", "user_kwame",
         "[SAMPLE] Spatial SIR-Vector Modeling of Dengue Outbreaks Under Shifting Monsoon Precipitation",
         "Increasing temperature fluctuations and irregular monsoon rainfall have expanded Aedes aegypti breeding zones into previously non-endemic elevated districts.",
         "Coupled meteorological-epidemiological models rarely account for localized water-storage behavior during dry spells.",
         json.dumps(["What is the minimum precipitation threshold that triggers exponential vector density spikes?"]),
         json.dumps(["H1: Threshold lagged precipitation (>80mm/week with 14-day lag) yields an R0 reproduction number > 1.85 in urban clusters."]),
         "Calibrate an empirical compartmental model to guide early municipal larvicide deployment.",
         "Averts critical hospital ward saturation in vulnerable secondary healthcare centers.",
         "Ross-Macdonald Mathematical Model of Mosquito-Borne Disease.",
         json.dumps(["SDG 3: Good Health and Well-Being", "SDG 11: Sustainable Cities"]),
         "in_review", 1)
    ]
    cur.executemany("""INSERT INTO research_ideas 
        (id, user_id, title, problem_statement, research_gap, research_questions, hypotheses, objectives, significance, theoretical_framework, sdg_alignment, status, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", ideas)

    # 5. Proposals
    proposals = [
        ("prop_climate_01", "idea_climate_agri", "user_bishnu",
         "[SAMPLE] Multi-Sensor Microclimate Optimization for High-Altitude Agroecosystems",
         "This investigation develops an open-source, edge-computed agro-meteorological monitoring and forecasting framework designed for high-altitude smallholder farmers.",
         "Mixed-method longitudinal quantitative field sensing and predictive statistical modeling (Random Forest & Ridge Regression).",
         "Validated 48-hour local agro-alert system, publication of open sensor dataset, and open policy recommendation brief.",
         38500.0, 18, 1, "approved",
         "Proposal demonstrates rigorous scientific merit, ethical community consent protocols, and measurable SDG alignment.", 1)
    ]
    cur.executemany("""INSERT INTO proposals 
        (id, idea_id, user_id, title, abstract, methodology, expected_outcomes, budget_estimate, duration_months, ethics_required, status, reviewer_comments, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", proposals)

    # 6. Projects
    projects = [
        ("proj_climate_2026", "user_bishnu",
         "[SAMPLE] Himalayan Agro-Climatic IoT Resilience & Predictive Modeling",
         "Empirical investigation of micro-topographic climate variables and machine learning predictive modeling for smallholder crop preservation.",
         "Climate & Environment", "data_analysis", 65, "2026-01-15", "2026-12-30", "Dr. Bishnu S. Rayamajhi", 4, 1),

        ("proj_solar_nano", "user_elena",
         "[SAMPLE] Degradation Kinematics of Double-Perovskite Photovoltaics in Tropical Humidity",
         "Laboratory-controlled accelerated aging tests of eco-friendly lead-free perovskite solar cells under 85% RH and thermal stress.",
         "Renewable Energy & Materials", "manuscript", 80, "2025-06-01", "2026-11-15", "Prof. Elena Rostova", 3, 1),

        ("proj_epidemic_ghana", "user_kwame",
         "[SAMPLE] Climate-Driven Vector Transmission Dynamics in West African Urban Corridors",
         "Field vector surveys and mathematical compartmental modeling to forecast seasonal epidemic peaks.",
         "Health Sciences", "ethics_review", 35, "2026-03-01", "2027-02-28", "Dr. Kwame Mensah", 5, 1)
    ]
    cur.executemany("""INSERT INTO projects 
        (id, user_id, title, description, category, stage, progress_percentage, start_date, target_end_date, lead_researcher, collaborators_count, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", projects)

    # 7. Tasks & Milestones
    tasks = [
        ("task_1", "proj_climate_2026", "Calibrate 15 barometric & hygrometer telemetry sensors", "Dr. Bishnu S. Rayamajhi", "completed", "high", "2026-02-15"),
        ("task_2", "proj_climate_2026", "Deploy LoRaWAN gateway in Mustang elevation transect", "Research Assistant", "completed", "urgent", "2026-03-30"),
        ("task_3", "proj_climate_2026", "Clean quarterly sensor telemetry and perform missing value imputation", "Dr. Bishnu S. Rayamajhi", "completed", "medium", "2026-07-20"),
        ("task_4", "proj_climate_2026", "Run bivariate correlation and linear regression analysis", "Sophia Chen, M.Sc.", "completed", "high", "2026-09-10"),
        ("task_5", "proj_climate_2026", "Draft manuscript Section 4: Results & Discussion", "Dr. Bishnu S. Rayamajhi", "in_progress", "urgent", "2026-11-01"),
        ("task_6", "proj_climate_2026", "Submit manuscript to Journal of Applied Meteorology & Climatology", "Dr. Bishnu S. Rayamajhi", "todo", "high", "2026-12-15")
    ]
    cur.executemany("INSERT INTO tasks (id, project_id, title, assigned_to, status, priority, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)", tasks)

    milestones = [
        ("ms_1", "proj_climate_2026", "Milestone 1: Field Sensor Deployment & Institutional Ethics Sign-off", "Community consent and physical node deployment completed", "2026-03-31", 1, "2026-03-28"),
        ("ms_2", "proj_climate_2026", "Milestone 2: 180-Day Continuous Climatic Dataset Acquired", "Zero major data gaps across 6 monitoring stations", "2026-08-01", 1, "2026-08-01"),
        ("ms_3", "proj_climate_2026", "Milestone 3: Statistical Verification and Model Benchmark", "R-squared > 0.82 achieved against historical baseline", "2026-10-15", 1, "2026-10-14"),
        ("ms_4", "proj_climate_2026", "Milestone 4: Peer-Reviewed Journal Submission & Policy Brief Delivery", "Dissemination to regional agricultural ministry", "2026-12-20", 0, None)
    ]
    cur.executemany("INSERT INTO milestones (id, project_id, title, description, due_date, completed, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)", milestones)

    # 8. Sample Datasets (Real tabular records for statistical engine)
    sample_agro_data = [
        {"elevation_m": 1850, "mean_temp_c": 19.4, "frost_days": 2, "soil_moisture_pct": 34.2, "crop_yield_kg": 420},
        {"elevation_m": 1920, "mean_temp_c": 18.8, "frost_days": 3, "soil_moisture_pct": 33.1, "crop_yield_kg": 405},
        {"elevation_m": 2040, "mean_temp_c": 17.5, "frost_days": 6, "soil_moisture_pct": 31.8, "crop_yield_kg": 380},
        {"elevation_m": 2150, "mean_temp_c": 16.9, "frost_days": 8, "soil_moisture_pct": 29.5, "crop_yield_kg": 362},
        {"elevation_m": 2280, "mean_temp_c": 15.6, "frost_days": 11, "soil_moisture_pct": 28.0, "crop_yield_kg": 335},
        {"elevation_m": 2350, "mean_temp_c": 14.8, "frost_days": 14, "soil_moisture_pct": 26.5, "crop_yield_kg": 310},
        {"elevation_m": 2480, "mean_temp_c": 13.9, "frost_days": 17, "soil_moisture_pct": 25.2, "crop_yield_kg": 285},
        {"elevation_m": 2590, "mean_temp_c": 12.8, "frost_days": 21, "soil_moisture_pct": 23.4, "crop_yield_kg": 255},
        {"elevation_m": 2720, "mean_temp_c": 11.5, "frost_days": 26, "soil_moisture_pct": 21.0, "crop_yield_kg": 220},
        {"elevation_m": 2850, "mean_temp_c": 10.2, "frost_days": 32, "soil_moisture_pct": 19.5, "crop_yield_kg": 180},
        {"elevation_m": 2980, "mean_temp_c": 9.1, "frost_days": 38, "soil_moisture_pct": 17.8, "crop_yield_kg": 145},
        {"elevation_m": 3100, "mean_temp_c": 8.0, "frost_days": 45, "soil_moisture_pct": 16.2, "crop_yield_kg": 110}
    ]
    
    datasets = [
        ("ds_agro_himalaya", "proj_climate_2026", "user_bishnu",
         "[SAMPLE] Mustang Agro-Meteorological Transect Telemetry (2026)",
         "Empirical multi-elevation observational dataset tracking temperature, frost frequency, soil moisture, and cereal crop yields across 12 monitoring stations.",
         json.dumps(sample_agro_data),
         json.dumps([
             {"name": "elevation_m", "type": "numeric", "unit": "meters"},
             {"name": "mean_temp_c", "type": "numeric", "unit": "°C"},
             {"name": "frost_days", "type": "numeric", "unit": "days/season"},
             {"name": "soil_moisture_pct", "type": "numeric", "unit": "%"},
             {"name": "crop_yield_kg", "type": "numeric", "unit": "kg/hectare"}
         ]),
         len(sample_agro_data), 1)
    ]
    cur.executemany("""INSERT INTO datasets 
        (id, project_id, user_id, name, description, data_json, columns_json, row_count, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", datasets)

    # 9. Verified Publications
    publications = [
        ("pub_1", "proj_climate_2026", "user_bishnu",
         "Empirical Evaluation of High-Altitude Agro-Climatic Gradient Sensitivity in Central Himalayas",
         "Rayamajhi, B. S., Rostova, E., & Sharma, K.",
         "Journal of Mountain Science and Sustainable Agriculture",
         2025, "10.1007/s11629-024-8841-x",
         "Investigating micro-elevation thermal inversion patterns and agricultural yields across high-relief valleys. Demonstrates high predictive utility of local surface lapse rate modeling.",
         "published", 47, 1, json.dumps(["SDG 2: Zero Hunger", "SDG 13: Climate Action"]), "https://doi.org/10.1007/s11629-024-8841-x", 1),

        ("pub_2", "proj_solar_nano", "user_elena",
         "Degradation Mechanisms in Lead-Free Bismuth-Halide Perovskites Under Extended Damp-Heat Cycling",
         "Rostova, E., Miller, J., & Chen, S.",
         "Advanced Energy Materials",
         2025, "10.1002/aenm.202403211",
         "Systematic structural degradation analysis of eco-friendly photovoltaic absorbers operating in tropical relative humidity conditions.",
         "published", 92, 1, json.dumps(["SDG 7: Affordable and Clean Energy", "SDG 9: Industry & Innovation"]), "https://doi.org/10.1002/aenm.202403211", 1),

        ("pub_3", "proj_epidemic_ghana", "user_kwame",
         "Spatial-Temporal Transmission Dynamics of Aedes-Borne Arboviruses in the Guinean Savannah",
         "Mensah, K., & Owusu-Addo, E.",
         "The Lancet Planetary Health",
         2024, "10.1016/S2542-5196(24)00119-2",
         "Multi-season longitudinal epidemiological cohort study mapping vector breeding densities under variable precipitation patterns.",
         "published", 114, 1, json.dumps(["SDG 3: Good Health and Well-Being"]), "https://doi.org/10.1016/S2542-5196(24)00119-2", 1)
    ]
    cur.executemany("""INSERT INTO publications 
        (id, project_id, user_id, title, authors, journal_or_conf, publication_year, doi, abstract, status, citation_count, open_access, sdg_alignment, pdf_url, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", publications)

    # 10. Learning Resources & Library
    resources = [
        ("res_stats_01", "Applied Biostatistics & Regression Diagnostics for Environmental Health", "Data Science", "course",
         "Harvard T.H. Chan School of Public Health OpenCourseWare", "Comprehensive video course covering linear regression assumptions, homoscedasticity testing, and multivariable model selection.",
         "https://pll.harvard.edu/course/biostatistics", json.dumps(["Statistics", "R Programming", "Regression"]), 1),

        ("res_meth_02", "Research Methodology & Quantitative Research Design: APA 7th Standard", "Methodology", "guide",
         "American Psychological Association Academic Publishing Hub", "Step-by-step framework for formulating falsifiable hypotheses, sampling frames, power analysis, and ethical participant protocols.",
         "https://apastyle.apa.org/instructional-aids", json.dumps(["Methodology", "Ethics", "APA7"]), 1),

        ("res_open_03", "FAIR Data Principles: Findable, Accessible, Interoperable, and Reusable", "Publication", "guide",
         "GO FAIR International Initiative & Scientific Data", "Operational guidelines for academic data stewardship, machine-readable metadata schemas, and repository archiving.",
         "https://www.go-fair.org/fair-principles/", json.dumps(["Open Science", "Data Stewardship", "Reproducibility"]), 1),

        ("res_sdg_04", "UN Sustainable Development Goals Research Impact Assessment Handbook", "Funding", "book",
         "United Nations Academic Impact (UNAI)", "Framework for measuring scientific contributions to 169 SDG targets with standardized qualitative and quantitative impact metrics.",
         "https://www.un.org/en/academic-impact", json.dumps(["SDGs", "Global Impact", "Policy Briefs"]), 1)
    ]
    cur.executemany("""INSERT INTO learning_resources 
        (id, title, category, resource_type, author_or_source, description, url, tags, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", resources)

    # 11. Funding Opportunities
    fundings = [
        ("fund_1", "Wellcome Trust International Climate & Health Research Fellowship", "Wellcome Trust", "$450,000 USD", "2026-11-30",
         "Early to mid-career researchers addressing ecological determinants of human pathogens.", "Health & Climate Sciences", "https://wellcome.org/grant-funding", "2026-09-01", "active"),

        ("fund_2", "Horizon Europe Global Ecological Transition & Resilience Grant", "European Research Council", "€1,200,000 EUR", "2027-01-15",
         "Consortium of at least 3 international institutional partners focused on clean energy or agro-resilience.", "Interdisciplinary STEM", "https://ec.europa.eu/info/funding-tenders", "2026-09-15", "active"),

        ("fund_3", "Global South Research Infrastructure Fellowship (IDRC)", "International Development Research Centre", "$85,000 USD", "2026-12-10",
         "Postdoctoral researchers affiliated with institutions in developing nations focusing on open scientific data.", "Open Science & AI", "https://www.idrc-crdi.ca/en/funding", "2026-08-20", "active")
    ]
    cur.executemany("""INSERT INTO funding_opportunities 
        (id, title, agency, amount_usd, deadline, eligibility, discipline, official_link, verified_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", fundings)

    # 12. Ethics Records
    ethics = [
        ("eth_2026_01", "proj_climate_2026", "user_bishnu", "approved", "IRB-TU-ENV-2026-089", 
         "Institutional Review Board for Earth & Agricultural Sciences", 1, 1, 0, 1, 
         "Informed consent protocols approved for all smallholder farming participants. Land sensor deployment inspected for environmental non-disturbance. AI model trained solely on verified physical telemetry.")
    ]
    cur.executemany("""INSERT INTO ethics_records 
        (id, project_id, user_id, status, protocol_num, irb_committee, informed_consent_verified, data_privacy_compliant, vulnerable_populations, responsible_ai_checklist, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", ethics)

    # 13. Impact Indicators (SDG Observatory)
    impacts = [
        ("imp_1", "proj_climate_2026", "SDG 2.4 (Sustainable Food Production)", "community_benefit",
         "Deployed open alert framework adopted by 3 local agricultural cooperatives in Mustang, reducing early frost crop damage by ~28% in trials.",
         "https://doi.org/10.1007/s11629-024-8841-x", 1250, 1),

        ("imp_2", "proj_climate_2026", "SDG 13.1 (Strengthen Adaptive Capacity to Climate Hazards)", "policy",
         "Contributed microclimatic gradient dataset to the National Climate Adaptation Directorate for regional policy updating.",
         "https://unfccc.int/nap", 45000, 1),

        ("imp_3", "proj_solar_nano", "SDG 7.a (Enhance International Cooperation in Clean Energy Research)", "technology_transfer",
         "Lead-free perovskite stabilization synthesis transferred to open academic clean-tech test facility in Cambridge and partner institutes.",
         "https://doi.org/10.1002/aenm.202403211", 500, 1)
    ]
    cur.executemany("""INSERT INTO impact_indicators 
        (id, project_id, sdg_target, impact_type, description, evidence_url, beneficiaries_count, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", impacts)

    # 14. Notifications & Audit Logs
    notifications = [
        ("notif_1", "user_bishnu", "Ethics Protocol Approved", "Protocol IRB-TU-ENV-2026-089 has received unconditional approval from the Review Board.", "success", 1),
        ("notif_2", "user_bishnu", "Collaboration Invitation", "Prof. Elena Rostova invited you to collaborate on Renewable Micro-Grid Optimization.", "collab", 0),
        ("notif_3", "user_bishnu", "Analysis Milestone Achieved", "OLS regression calculations on Mustang dataset completed with R² = 0.985 (p < 0.001).", "info", 0)
    ]
    cur.executemany("INSERT INTO notifications (id, user_id, title, message, type, is_read) VALUES (?, ?, ?, ?, ?, ?)", notifications)

    audit_logs = [
        ("log_1", "user_bishnu", "PROJECT_CREATE", "projects", "proj_climate_2026", "Initialized Himalayan Agro-Climatic IoT Resilience project"),
        ("log_2", "user_bishnu", "DATASET_UPLOAD", "datasets", "ds_agro_himalaya", "Uploaded and validated 12 station telemetry records"),
        ("log_3", "user_elena", "PROPOSAL_APPROVAL", "proposals", "prop_climate_01", "Supervisor review signed off with favorable score")
    ]
    cur.executemany("INSERT INTO audit_logs (id, user_id, action, entity, entity_id, details) VALUES (?, ?, ?, ?, ?, ?)", audit_logs)

    conn.commit()
    conn.close()
    print("Database successfully seeded with academic demonstration projects, datasets, and verified references.")

if __name__ == "__main__":
    seed_database()
