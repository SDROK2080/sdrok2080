"""
RI-GI Nexus Intelligent HTTP Application Server
Provides RESTful APIs for all 14 Modules, Static Frontend Delivery,
Scientific Analytics (Descriptive stats, Pearson/Spearman, OLS Regression, t-tests),
Simulation Studio (SIR Epidemic, Climate CO2 Forcing),
AI Research Assistant Engine (Rigorous academic synthesis without fabricated citations),
Publication Studio (APA 7th formatting, Exportable Markdown/HTML),
and Global SDG Impact Observatory.
"""

import http.server
import socketserver
import json
import urllib.parse
import sqlite3
import os
import uuid
import datetime
from scientific_engine import ScientificEngine
from database import DB_PATH

PORT = 8085

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class NexusRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.serve_file("index.html", "text/html")
        elif path.startswith("/api/"):
            self.handle_api_get(path, params)
        else:
            # Serve local static assets (CSS, JS, images)
            local_path = os.path.join(os.path.dirname(__file__), path.lstrip("/"))
            if os.path.exists(local_path) and os.path.isfile(local_path):
                ext = os.path.splitext(local_path)[1]
                content_types = {
                    ".html": "text/html",
                    ".css": "text/css",
                    ".js": "application/javascript",
                    ".json": "application/json",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".svg": "image/svg+xml"
                }
                self.serve_file(local_path, content_types.get(ext, "application/octet-stream"))
            else:
                self.send_error(404, f"File {path} not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            body = json.loads(post_body) if post_body else {}
        except Exception:
            body = {}

        self.handle_api_post(path, body)

    def serve_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    # -----------------------------
    # API GET ROUTING
    # -----------------------------
    def handle_api_get(self, path, params):
        conn = get_db()
        cur = conn.cursor()

        try:
            if path == "/api/stats/overview":
                # Aggregate metrics for the Researcher Dashboard
                cur.execute("SELECT COUNT(*) FROM projects")
                total_projects = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM projects WHERE stage != 'published'")
                active_projects = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM publications WHERE status = 'published'")
                published_papers = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM proposals WHERE status = 'under_review' OR status = 'submitted'")
                proposals_review = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM milestones WHERE completed = 1")
                milestones_completed = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM collaborations WHERE status = 'pending'")
                collab_invites = cur.fetchone()[0]

                cur.execute("SELECT SUM(citation_count) FROM publications")
                citations_sum = cur.fetchone()[0] or 0

                cur.execute("SELECT SUM(beneficiaries_count) FROM impact_indicators")
                beneficiaries_sum = cur.fetchone()[0] or 0

                # Recent projects
                cur.execute("SELECT id, title, category, stage, progress_percentage, target_end_date FROM projects ORDER BY created_at DESC LIMIT 5")
                recent_projects = [dict(row) for row in cur.fetchall()]

                # Upcoming tasks
                cur.execute("SELECT id, project_id, title, priority, due_date, status FROM tasks WHERE status != 'completed' ORDER BY due_date ASC LIMIT 5")
                upcoming_tasks = [dict(row) for row in cur.fetchall()]

                # SDG impact summary
                cur.execute("SELECT sdg_target, COUNT(*) as count, SUM(beneficiaries_count) as total_reached FROM impact_indicators GROUP BY sdg_target")
                sdg_stats = [dict(row) for row in cur.fetchall()]

                self.send_json({
                    "success": True,
                    "metrics": {
                        "total_projects": total_projects,
                        "active_projects": active_projects,
                        "published_papers": published_papers,
                        "proposals_awaiting_review": proposals_review,
                        "milestones_completed": milestones_completed,
                        "collaboration_invitations": collab_invites,
                        "total_citations": citations_sum,
                        "documented_beneficiaries": beneficiaries_sum
                    },
                    "recent_projects": recent_projects,
                    "upcoming_tasks": upcoming_tasks,
                    "sdg_impact_summary": sdg_stats
                })

            elif path == "/api/ideas":
                cur.execute("SELECT * FROM research_ideas ORDER BY created_at DESC")
                rows = [dict(row) for row in cur.fetchall()]
                for r in rows:
                    r["research_questions"] = json.loads(r["research_questions"]) if r.get("research_questions") else []
                    r["hypotheses"] = json.loads(r["hypotheses"]) if r.get("hypotheses") else []
                    r["sdg_alignment"] = json.loads(r["sdg_alignment"]) if r.get("sdg_alignment") else []
                self.send_json({"success": True, "ideas": rows})

            elif path == "/api/projects":
                cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
                projects = [dict(row) for row in cur.fetchall()]
                # Enrich with task and milestone counts
                for p in projects:
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (p["id"],))
                    p["total_tasks"] = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'completed'", (p["id"],))
                    p["completed_tasks"] = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM milestones WHERE project_id = ?", (p["id"],))
                    p["milestone_count"] = cur.fetchone()[0]
                self.send_json({"success": True, "projects": projects})

            elif path.startswith("/api/projects/") and path.endswith("/details"):
                proj_id = path.split("/")[3]
                cur.execute("SELECT * FROM projects WHERE id = ?", (proj_id,))
                proj = cur.fetchone()
                if not proj:
                    self.send_json({"error": "Project not found"}, 404)
                    return
                p_dict = dict(proj)

                cur.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY due_date ASC", (proj_id,))
                p_dict["tasks"] = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT * FROM milestones WHERE project_id = ? ORDER BY due_date ASC", (proj_id,))
                p_dict["milestones"] = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT * FROM datasets WHERE project_id = ?", (proj_id,))
                p_dict["datasets"] = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT * FROM ethics_records WHERE project_id = ?", (proj_id,))
                p_dict["ethics"] = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT * FROM impact_indicators WHERE project_id = ?", (proj_id,))
                p_dict["impacts"] = [dict(row) for row in cur.fetchall()]

                self.send_json({"success": True, "project": p_dict})

            elif path == "/api/proposals":
                cur.execute("SELECT * FROM proposals ORDER BY created_at DESC")
                rows = [dict(row) for row in cur.fetchall()]
                self.send_json({"success": True, "proposals": rows})

            elif path == "/api/datasets":
                cur.execute("SELECT id, project_id, user_id, name, description, columns_json, row_count, is_sample, created_at FROM datasets ORDER BY created_at DESC")
                rows = [dict(row) for row in cur.fetchall()]
                for r in rows:
                    r["columns"] = json.loads(r["columns_json"]) if r.get("columns_json") else []
                self.send_json({"success": True, "datasets": rows})

            elif path.startswith("/api/datasets/") and path.endswith("/data"):
                ds_id = path.split("/")[3]
                cur.execute("SELECT * FROM datasets WHERE id = ?", (ds_id,))
                row = cur.fetchone()
                if not row:
                    self.send_json({"error": "Dataset not found"}, 404)
                    return
                d_dict = dict(row)
                d_dict["records"] = json.loads(d_dict["data_json"])
                d_dict["columns"] = json.loads(d_dict["columns_json"])
                del d_dict["data_json"]
                del d_dict["columns_json"]
                self.send_json({"success": True, "dataset": d_dict})

            elif path == "/api/publications":
                cur.execute("SELECT * FROM publications ORDER BY publication_year DESC, created_at DESC")
                rows = [dict(row) for row in cur.fetchall()]
                for r in rows:
                    r["sdg_alignment"] = json.loads(r["sdg_alignment"]) if r.get("sdg_alignment") else []
                self.send_json({"success": True, "publications": rows})

            elif path == "/api/learning-resources":
                cur.execute("SELECT * FROM learning_resources ORDER BY created_at DESC")
                rows = [dict(row) for row in cur.fetchall()]
                for r in rows:
                    r["tags"] = json.loads(r["tags"]) if r.get("tags") else []
                self.send_json({"success": True, "resources": rows})

            elif path == "/api/funding":
                cur.execute("SELECT * FROM funding_opportunities ORDER BY deadline ASC")
                rows = [dict(row) for row in cur.fetchall()]
                self.send_json({"success": True, "opportunities": rows})

            elif path == "/api/researchers":
                cur.execute("""
                    SELECT u.id, u.name, u.email, u.institution, u.avatar, u.role,
                           p.title, p.bio, p.orcid_id, p.field_of_study, p.research_interests,
                           p.h_index, p.total_citations, p.website, p.available_for_collab
                    FROM users u
                    LEFT JOIN researcher_profiles p ON u.id = p.user_id
                    WHERE u.role != 'administrator'
                """)
                rows = [dict(row) for row in cur.fetchall()]
                for r in rows:
                    r["research_interests"] = json.loads(r["research_interests"]) if r.get("research_interests") else []
                self.send_json({"success": True, "researchers": rows})

            elif path == "/api/impact/observatory":
                cur.execute("""
                    SELECT i.*, p.title as project_title, p.category as project_category
                    FROM impact_indicators i
                    JOIN projects p ON i.project_id = p.id
                    ORDER BY i.created_at DESC
                """)
                indicators = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT sdg_target, count(*) as count, sum(beneficiaries_count) as total_beneficiaries FROM impact_indicators GROUP BY sdg_target")
                by_sdg = [dict(row) for row in cur.fetchall()]

                cur.execute("SELECT impact_type, count(*) as count FROM impact_indicators GROUP BY impact_type")
                by_type = [dict(row) for row in cur.fetchall()]

                self.send_json({
                    "success": True,
                    "indicators": indicators,
                    "sdg_distribution": by_sdg,
                    "type_distribution": by_type
                })

            elif path == "/api/ethics":
                cur.execute("""
                    SELECT e.*, p.title as project_title
                    FROM ethics_records e
                    JOIN projects p ON e.project_id = p.id
                """)
                records = [dict(row) for row in cur.fetchall()]
                self.send_json({"success": True, "records": records})

            elif path == "/api/notifications":
                cur.execute("SELECT * FROM notifications ORDER BY created_at DESC")
                records = [dict(row) for row in cur.fetchall()]
                self.send_json({"success": True, "notifications": records})

            elif path == "/api/audit-logs":
                cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50")
                records = [dict(row) for row in cur.fetchall()]
                self.send_json({"success": True, "logs": records})

            else:
                self.send_json({"error": f"API endpoint '{path}' not found"}, 404)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    # -----------------------------
    # API POST ROUTING
    # -----------------------------
    def handle_api_post(self, path, body):
        conn = get_db()
        cur = conn.cursor()

        try:
            # 1. Scientific Analysis Runner
            if path == "/api/analysis/run":
                analysis_type = body.get("type")
                dataset_id = body.get("dataset_id")
                cur.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
                row = cur.fetchone()
                if not row:
                    self.send_json({"error": "Dataset not found"}, 404)
                    return
                records = json.loads(row["data_json"])

                if analysis_type == "descriptive":
                    col = body.get("column")
                    vals = [r.get(col) for r in records if r.get(col) is not None]
                    res = ScientificEngine.calculate_descriptive(vals, col)

                elif analysis_type == "correlation":
                    x_col = body.get("x_col")
                    y_col = body.get("y_col")
                    x_vals = [r.get(x_col) for r in records]
                    y_vals = [r.get(y_col) for r in records]
                    res = ScientificEngine.calculate_correlation(x_vals, y_vals, x_col, y_col)

                elif analysis_type == "regression":
                    x_col = body.get("x_col")
                    y_col = body.get("y_col")
                    x_vals = [r.get(x_col) for r in records]
                    y_vals = [r.get(y_col) for r in records]
                    res = ScientificEngine.calculate_regression(x_vals, y_vals, x_col, y_col)

                elif analysis_type == "ttest":
                    col1 = body.get("col1")
                    test_kind = body.get("test_kind", "one_sample")
                    mu = float(body.get("mu", 0))
                    vals1 = [r.get(col1) for r in records]
                    col2 = body.get("col2")
                    vals2 = [r.get(col2) for r in records] if col2 else None
                    res = ScientificEngine.calculate_ttest(vals1, vals2, mu, test_kind)

                else:
                    self.send_json({"error": "Invalid analysis type"}, 400)
                    return

                # Record analysis run in database
                run_id = f"run_{uuid.uuid4().hex[:8]}"
                cur.execute("""
                    INSERT INTO analysis_runs (id, dataset_id, user_id, analysis_type, parameters, results_json, interpretation, limitations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (run_id, dataset_id, "user_bishnu", analysis_type, json.dumps(body), json.dumps(res), res.get("interpretation", ""), res.get("limitations", "")))
                
                # Log audit
                cur.execute("INSERT INTO audit_logs (id, user_id, action, entity, entity_id, details) VALUES (?, ?, ?, ?, ?, ?)",
                            (f"log_{uuid.uuid4().hex[:8]}", "user_bishnu", "ANALYSIS_RUN", "analysis_runs", run_id, f"Executed {analysis_type} calculation"))
                conn.commit()

                self.send_json({"success": True, "run_id": run_id, "results": res})

            # 2. Simulation Studio Engine
            elif path == "/api/simulation/run":
                model_type = body.get("model_type")
                if model_type == "sir_model":
                    total_pop = int(body.get("total_pop", 10000))
                    init_inf = int(body.get("initial_infected", 10))
                    beta = float(body.get("beta", 0.35))
                    gamma = float(body.get("gamma", 0.1))
                    days = int(body.get("days", 100))
                    sim_result = ScientificEngine.simulate_sir_model(total_pop, init_inf, beta, gamma, days)
                elif model_type == "climate_co2":
                    init_co2 = float(body.get("initial_co2", 420.0))
                    growth_rate = float(body.get("growth_rate", 0.015))
                    sensitivity = float(body.get("climate_sensitivity", 3.0))
                    years = int(body.get("years", 50))
                    sim_result = ScientificEngine.simulate_climate_co2(init_co2, growth_rate, sensitivity, years)
                else:
                    self.send_json({"error": "Unknown simulation model"}, 400)
                    return

                # Save experiment record
                exp_id = f"exp_{uuid.uuid4().hex[:8]}"
                cur.execute("""
                    INSERT INTO experiments (id, project_id, user_id, title, model_type, parameters_json, results_json, conclusions, is_sample)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (exp_id, body.get("project_id", "proj_climate_2026"), "user_bishnu", body.get("title", f"Simulation of {model_type}"), model_type, json.dumps(body), json.dumps(sim_result), sim_result.get("interpretation", ""), 0))
                conn.commit()

                self.send_json({"success": True, "experiment_id": exp_id, "simulation": sim_result})

            # 3. AI Academic Assistant Query Engine
            elif path == "/api/ai-assistant/query":
                task = body.get("task")
                prompt = body.get("prompt", "")
                context = body.get("context", "")

                ai_response = self.generate_academic_ai_response(task, prompt, context)
                self.send_json({"success": True, "response": ai_response})

            # 4. Create Research Idea
            elif path == "/api/ideas/create":
                idea_id = f"idea_{uuid.uuid4().hex[:8]}"
                title = body.get("title", "Untitled Research Idea")
                prob = body.get("problem_statement", "")
                gap = body.get("research_gap", "")
                rqs = json.dumps(body.get("research_questions", []))
                hyp = json.dumps(body.get("hypotheses", []))
                objs = body.get("objectives", "")
                signif = body.get("significance", "")
                framework = body.get("theoretical_framework", "")
                sdgs = json.dumps(body.get("sdg_alignment", []))

                cur.execute("""
                    INSERT INTO research_ideas (id, user_id, title, problem_statement, research_gap, research_questions, hypotheses, objectives, significance, theoretical_framework, sdg_alignment, status, is_sample)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', 0)
                """, (idea_id, "user_bishnu", title, prob, gap, rqs, hyp, objs, signif, framework, sdgs))
                
                cur.execute("INSERT INTO audit_logs (id, user_id, action, entity, entity_id, details) VALUES (?, ?, ?, ?, ?, ?)",
                            (f"log_{uuid.uuid4().hex[:8]}", "user_bishnu", "IDEA_CREATE", "research_ideas", idea_id, f"Created research idea '{title}'"))
                conn.commit()
                self.send_json({"success": True, "idea_id": idea_id, "message": "Research idea saved successfully."})

            # 5. Convert Idea to Formal Proposal
            elif path == "/api/ideas/convert-to-proposal":
                idea_id = body.get("idea_id")
                cur.execute("SELECT * FROM research_ideas WHERE id = ?", (idea_id,))
                idea = cur.fetchone()
                if not idea:
                    self.send_json({"error": "Idea not found"}, 404)
                    return
                
                prop_id = f"prop_{uuid.uuid4().hex[:8]}"
                cur.execute("""
                    INSERT INTO proposals (id, idea_id, user_id, title, abstract, methodology, expected_outcomes, budget_estimate, duration_months, ethics_required, status, is_sample)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', 0)
                """, (prop_id, idea_id, "user_bishnu", f"Proposal: {idea['title']}", idea["problem_statement"], "Mixed-methods empirical investigation", idea["significance"], 25000.0, 12, 1))

                cur.execute("UPDATE research_ideas SET status = 'converted_to_proposal' WHERE id = ?", (idea_id,))
                conn.commit()
                self.send_json({"success": True, "proposal_id": prop_id, "message": "Successfully formulated proposal from idea."})

            # 6. Create Research Project
            elif path == "/api/projects/create":
                proj_id = f"proj_{uuid.uuid4().hex[:8]}"
                title = body.get("title", "New Research Project")
                desc = body.get("description", "")
                cat = body.get("category", "Interdisciplinary STEM")
                start_date = body.get("start_date", datetime.date.today().isoformat())
                target_date = body.get("target_end_date", (datetime.date.today() + datetime.timedelta(days=365)).isoformat())

                cur.execute("""
                    INSERT INTO projects (id, user_id, title, description, category, stage, progress_percentage, start_date, target_end_date, lead_researcher, collaborators_count, is_sample)
                    VALUES (?, ?, ?, ?, ?, 'idea', 5, ?, ?, 'Dr. Bishnu S. Rayamajhi', 1, 0)
                """, (proj_id, "user_bishnu", title, desc, cat, start_date, target_date))

                # Add initial default milestone
                cur.execute("""
                    INSERT INTO milestones (id, project_id, title, description, due_date, completed)
                    VALUES (?, ?, 'Literature Review & Ethical Clearance', 'Establish theoretical foundations and IRB documentation', ?, 0)
                """, (f"ms_{uuid.uuid4().hex[:8]}", proj_id, target_date))

                conn.commit()
                self.send_json({"success": True, "project_id": proj_id, "message": "Project created successfully."})

            # 7. Add Project Task
            elif path == "/api/tasks/create":
                task_id = f"task_{uuid.uuid4().hex[:8]}"
                proj_id = body.get("project_id")
                title = body.get("title")
                priority = body.get("priority", "medium")
                due = body.get("due_date", datetime.date.today().isoformat())

                cur.execute("""
                    INSERT INTO tasks (id, project_id, title, assigned_to, status, priority, due_date)
                    VALUES (?, ?, ?, 'Dr. Bishnu S. Rayamajhi', 'todo', ?, ?)
                """, (task_id, proj_id, title, priority, due))
                conn.commit()
                self.send_json({"success": True, "task_id": task_id})

            # 8. Update Task Status
            elif path == "/api/tasks/update-status":
                task_id = body.get("task_id")
                status = body.get("status")
                cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
                conn.commit()
                self.send_json({"success": True})

            # 9. Send Collaboration Request
            elif path == "/api/collaborations/request":
                collab_id = f"collab_{uuid.uuid4().hex[:8]}"
                receiver_id = body.get("receiver_id")
                proj_title = body.get("project_title")
                msg = body.get("message")

                cur.execute("""
                    INSERT INTO collaborations (id, requester_id, receiver_id, project_title, proposal_message, status)
                    VALUES (?, 'user_bishnu', ?, ?, ?, 'pending')
                """, (collab_id, receiver_id, proj_title, msg))

                # Notify recipient
                cur.execute("""
                    INSERT INTO notifications (id, user_id, title, message, type)
                    VALUES (?, ?, 'New Collaboration Request', ?, 'collab')
                """, (f"notif_{uuid.uuid4().hex[:8]}", receiver_id, f"Dr. Bishnu S. Rayamajhi requested to collaborate on '{proj_title}'."))

                conn.commit()
                self.send_json({"success": True, "message": "Collaboration invitation delivered securely."})

            # 10. Record Impact Indicator
            elif path == "/api/impact/record":
                imp_id = f"imp_{uuid.uuid4().hex[:8]}"
                proj_id = body.get("project_id", "proj_climate_2026")
                sdg_target = body.get("sdg_target")
                impact_type = body.get("impact_type")
                desc = body.get("description")
                evidence = body.get("evidence_url", "")
                count = int(body.get("beneficiaries_count", 0))

                cur.execute("""
                    INSERT INTO impact_indicators (id, project_id, sdg_target, impact_type, description, evidence_url, beneficiaries_count, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (imp_id, proj_id, sdg_target, impact_type, desc, evidence, count))
                conn.commit()
                self.send_json({"success": True, "impact_id": imp_id, "message": "Impact evidence logged into SDG Observatory."})

            # 11. Add User Uploaded Dataset (CSV/JSON tabular data)
            elif path == "/api/datasets/upload":
                name = body.get("name", "User Dataset")
                description = body.get("description", "")
                raw_records = body.get("records", [])
                
                if not raw_records or not isinstance(raw_records, list):
                    self.send_json({"error": "Dataset must contain at least 1 record in JSON array format"}, 400)
                    return

                # Detect columns
                first_row = raw_records[0]
                cols = []
                for k, v in first_row.items():
                    col_type = "numeric" if isinstance(v, (int, float)) else "text"
                    cols.append({"name": k, "type": col_type, "unit": ""})

                ds_id = f"ds_{uuid.uuid4().hex[:8]}"
                cur.execute("""
                    INSERT INTO datasets (id, project_id, user_id, name, description, data_json, columns_json, row_count, is_sample)
                    VALUES (?, 'proj_climate_2026', 'user_bishnu', ?, ?, ?, ?, ?, 0)
                """, (ds_id, name, description, json.dumps(raw_records), json.dumps(cols), len(raw_records)))
                conn.commit()
                self.send_json({"success": True, "dataset_id": ds_id, "columns": cols, "row_count": len(raw_records)})

            else:
                self.send_json({"error": f"POST endpoint '{path}' not recognized"}, 404)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def generate_academic_ai_response(self, task, prompt, context=""):
        """
        Synthesizes structured academic assistance adhering to strict integrity guidelines:
        - Clearly distinguishes verified scientific evidence from AI suggestions
        - Never fabricates fake DOIs, authors, or statistical outputs
        - Explains statistical techniques, methodological frameworks, and research design
        """
        if task == "refine_questions":
            return {
                "category": "Research Question & Hypothesis Refinement",
                "label": "AI Suggestion (Requires Researcher Verification)",
                "refined_questions": [
                    f"To what extent does {prompt.strip()} influence localized variance in high-altitude terrain?",
                    f"What is the moderating role of seasonal micro-climatic shifts on {prompt.strip()}?",
                    f"How can multi-station observational telemetry minimize prediction uncertainty in {prompt.strip()}?"
                ],
                "falsifiable_hypotheses": [
                    f"H1 (Directional): An increase in {prompt.strip()} is negatively correlated with frost-induced yield loss (alpha = 0.05).",
                    f"H0 (Null): Variation in {prompt.strip()} demonstrates no statistically significant relationship with the response metric."
                ],
                "methodological_advice": "Ensure operational definitions for all continuous metrics. Conduct power analysis (G*Power) to determine necessary sample size prior to data acquisition."
            }

        elif task == "outline_literature":
            return {
                "category": "Literature Review Conceptual Outline",
                "label": "AI Suggestion (Align with Verified Databases: Crossref, OpenAlex, PubMed)",
                "sections": [
                    {
                        "theme": "1. Theoretical Foundations & Paradigm Overview",
                        "focus": f"Examine foundational literature regarding {prompt.strip()}. Synthesize classical thermodynamic or socio-technical models."
                    },
                    {
                        "theme": "2. Current Methodological Approaches & Limitations",
                        "focus": "Critically contrast satellite remote sensing (macro-resolution) versus localized IoT in-situ sensors (micro-resolution)."
                    },
                    {
                        "theme": "3. The Documented Research Gap",
                        "focus": "Identify spatial scale disconnects and inadequate empirical validation in mountainous or underserved geographic regions."
                    },
                    {
                        "theme": "4. Conceptual Framework Formulation",
                        "focus": "Illustrate interaction terms between independent environmental factors and target socioeconomic or biological outcomes."
                    }
                ],
                "integrity_notice": "Antigravity AI does not fabricate author names or DOIs. Please query verified databases via the Research Library to retrieve validated sources."
            }

        elif task == "statistical_selection":
            return {
                "category": "Methodological & Statistical Technique Selector",
                "label": "Methodological Guidance",
                "recommended_technique": "Multivariate Ordinary Least Squares (OLS) or Hierarchical Mixed-Effects Modeling",
                "assumptions_checklist": [
                    "Continuous outcome variable with normally distributed residuals (assess via Shapiro-Wilk test and Q-Q plots).",
                    "Independence of observations (Durbin-Watson d-statistic between 1.5 and 2.5).",
                    "Homoscedasticity of variance (verify with Breusch-Pagan test).",
                    "Absence of severe multicollinearity (Variance Inflation Factor VIF < 5.0)."
                ],
                "alternative_non_parametric": "If normality or equal variance is violated, employ Spearman Rank Correlation or Huber Robust Regression."
            }

        elif task == "academic_writing_polish":
            return {
                "category": "Academic Writing & Precision Synthesis",
                "label": "Stylistic & Precision Enhancements",
                "input_snippet": prompt,
                "suggestions": [
                    "Replace passive constructions with precise scientific active voice where appropriate.",
                    "Ensure exact reporting of test statistics: e.g., t(11) = 4.12, p = .002, R² = .84.",
                    "Explicitly state limitations regarding generalizability and measurement boundary conditions."
                ],
                "sample_abstract_draft": f"This investigation addresses critical knowledge gaps in {prompt.strip()}. Utilizing an empirical quantitative methodology, observational data were evaluated using validated parametric regression and hypothesis tests. Findings reveal key predictive determinants, offering reproducible foundations for evidence-based policy formulation."
            }

        else:
            return {
                "category": "General Academic Research Guidance",
                "label": "Evidence-Based Guidance",
                "guidance": f"Regarding your inquiry on '{prompt}': Maintain clear alignment between research questions, chosen methodology, and reproducible data workflows. Verify all citations against primary peer-reviewed literature."
            }

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = socketserver.TCPServer(server_address, NexusRequestHandler)
    print(f"================================================================")
    print(f"RI-GI Nexus Platform Running at http://127.0.0.1:{PORT}")
    print(f"Mission: Research • Innovation • Global Impact")
    print(f"Tagline: 'Empowering Researchers for a Better Tomorrow.'")
    print(f"================================================================")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
