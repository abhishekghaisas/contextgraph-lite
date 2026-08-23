"""
Seed CognoDB with a realistic-looking org: people, teams, projects, tasks,
documents, messages, meetings and tools, connected the way real work is.

Usage:
    cp .env.example .env   # fill in your CognoDB credentials
    pip install -r requirements.txt
    python scripts/seed.py

Safe to re-run: every write uses MERGE on a stable id, so re-running just
updates properties instead of duplicating nodes.
"""
import os
import random
import uuid

from dotenv import find_dotenv, load_dotenv
from faker import Faker
from neo4j import GraphDatabase, basic_auth

load_dotenv(find_dotenv(usecwd=True))

fake = Faker()
random.seed(42)
Faker.seed(42)

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

N_PEOPLE = 40
N_TEAMS = 6
N_PROJECTS = 10
N_TASKS = 120
N_DOCS = 150
N_MESSAGES = 400
N_MEETINGS = 50
TOOLS = ["Slack", "Gmail", "Jira", "Salesforce", "Confluence", "Google Drive"]

CONSTRAINTS = [
    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT team_id IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT msg_id IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT meeting_id IF NOT EXISTS FOR (m:Meeting) REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT tool_id IF NOT EXISTS FOR (t:Tool) REQUIRE t.id IS UNIQUE",
]


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def gen_teams():
    names = ["Platform", "Growth", "Data", "Design", "Sales Eng", "Customer Success"]
    return [{"id": new_id("team"), "name": n} for n in names[:N_TEAMS]]


def gen_people(teams):
    return [
        {
            "id": new_id("person"),
            "name": fake.name(),
            "title": fake.job(),
            "team_id": random.choice(teams)["id"],
            "joined_at": fake.date_between(start_date="-3y", end_date="-1M").isoformat(),
        }
        for _ in range(N_PEOPLE)
    ]


def gen_projects():
    statuses = ["active", "active", "active", "on_hold", "completed"]
    return [
        {
            "id": new_id("project"),
            "name": fake.bs().title(),
            "status": random.choice(statuses),
            "started_at": fake.date_between(start_date="-2y", end_date="-2M").isoformat(),
        }
        for _ in range(N_PROJECTS)
    ]


def gen_memberships(people, projects):
    """Each person works on 1-3 projects — this is the backbone the rest hangs off."""
    memberships = []
    for p in people:
        for proj in random.sample(projects, k=random.randint(1, 3)):
            memberships.append(
                {
                    "person_id": p["id"],
                    "project_id": proj["id"],
                    "role": random.choice(["contributor", "lead", "reviewer"]),
                }
            )
    return memberships


def gen_tasks(projects, memberships):
    statuses = ["todo", "in_progress", "in_progress", "done", "blocked"]
    priorities = ["low", "medium", "high"]

    proj_to_people: dict[str, list[str]] = {}
    for m in memberships:
        proj_to_people.setdefault(m["project_id"], []).append(m["person_id"])

    tasks = []
    for _ in range(N_TASKS):
        proj = random.choice(projects)
        candidates = proj_to_people.get(proj["id"])
        tasks.append(
            {
                "id": new_id("task"),
                "title": fake.catch_phrase(),
                "status": random.choice(statuses),
                "priority": random.choice(priorities),
                "project_id": proj["id"],
                "assignee_id": random.choice(candidates) if candidates else None,
                "created_at": fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            }
        )
    return tasks


def gen_blocks(tasks):
    """Wire ~15% of within-project task pairs as blockers, so blocker-chain queries return something real."""
    by_project: dict[str, list[dict]] = {}
    for t in tasks:
        by_project.setdefault(t["project_id"], []).append(t)

    blocks = []
    for proj_tasks in by_project.values():
        if len(proj_tasks) < 2:
            continue
        n_links = max(1, int(len(proj_tasks) * 0.15))
        for _ in range(n_links):
            a, b = random.sample(proj_tasks, 2)
            if a["id"] != b["id"]:
                blocks.append({"blocker_id": a["id"], "blocked_id": b["id"]})
    return blocks


def gen_documents(people, projects, tasks):
    docs = []
    for _ in range(N_DOCS):
        author = random.choice(people)
        target_type = random.choice(["project", "task"])
        target_id = (
            random.choice(projects)["id"] if target_type == "project" else random.choice(tasks)["id"]
        )
        docs.append(
            {
                "id": new_id("doc"),
                "title": f"{fake.bs().title()} Notes",
                "type": random.choice(["spec", "doc", "slide", "report"]),
                "author_id": author["id"],
                "target_type": target_type,
                "target_id": target_id,
                "updated_at": fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            }
        )
    return docs


def gen_messages(people, projects, tasks):
    messages = []
    for _ in range(N_MESSAGES):
        sender = random.choice(people)
        proj = random.choice(projects)
        mention_type = random.choice(["person", "task", None])
        mention_id = None
        if mention_type == "person":
            mention_id = random.choice(people)["id"]
        elif mention_type == "task":
            mention_id = random.choice(tasks)["id"]
        messages.append(
            {
                "id": new_id("msg"),
                "channel": f"#{proj['name'].split()[0].lower()}",
                "text_snippet": fake.sentence(),
                "sender_id": sender["id"],
                "project_id": proj["id"],
                "mention_type": mention_type,
                "mention_id": mention_id,
                "sent_at": fake.date_time_between(start_date="-6M", end_date="now").isoformat(),
            }
        )
    return messages


def gen_meetings(people, projects):
    meetings = []
    for _ in range(N_MEETINGS):
        proj = random.choice(projects)
        attendees = random.sample(people, k=random.randint(2, 6))
        meetings.append(
            {
                "id": new_id("meeting"),
                "title": f"{proj['name']} sync",
                "project_id": proj["id"],
                "attendee_ids": [p["id"] for p in attendees],
                "held_at": fake.date_time_between(start_date="-6M", end_date="now").isoformat(),
            }
        )
    return meetings


def gen_tools():
    return [{"id": new_id("tool"), "name": name} for name in TOOLS]


def gen_project_tools(projects, tools):
    return [
        {"project_id": proj["id"], "tool_id": tool["id"]}
        for proj in projects
        for tool in random.sample(tools, k=random.randint(2, 4))
    ]


def run(driver):
    with driver.session() as session:
        for stmt in CONSTRAINTS:
            session.run(stmt)

        teams = gen_teams()
        session.run(
            "UNWIND $rows AS row MERGE (t:Team {id: row.id}) SET t.name = row.name",
            rows=teams,
        )

        people = gen_people(teams)
        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Person {id: row.id})
            SET p.name = row.name, p.title = row.title, p.joined_at = row.joined_at
            WITH p, row
            MATCH (t:Team {id: row.team_id})
            MERGE (p)-[:MEMBER_OF]->(t)
            """,
            rows=people,
        )

        projects = gen_projects()
        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Project {id: row.id})
            SET p.name = row.name, p.status = row.status, p.started_at = row.started_at
            """,
            rows=projects,
        )

        memberships = gen_memberships(people, projects)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (p:Person {id: row.person_id}), (proj:Project {id: row.project_id})
            MERGE (p)-[r:WORKS_ON]->(proj)
            SET r.role = row.role
            """,
            rows=memberships,
        )

        tasks = gen_tasks(projects, memberships)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (proj:Project {id: row.project_id})
            MERGE (t:Task {id: row.id})
            SET t.title = row.title, t.status = row.status,
                t.priority = row.priority, t.created_at = row.created_at
            MERGE (t)-[:PART_OF]->(proj)
            """,
            rows=tasks,
        )
        tasks_with_assignee = [t for t in tasks if t["assignee_id"]]
        session.run(
            """
            UNWIND $rows AS row
            MATCH (t:Task {id: row.id}), (a:Person {id: row.assignee_id})
            MERGE (t)-[:ASSIGNED_TO]->(a)
            """,
            rows=tasks_with_assignee,
        )

        blocks = gen_blocks(tasks)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (a:Task {id: row.blocker_id}), (b:Task {id: row.blocked_id})
            MERGE (a)-[:BLOCKS]->(b)
            """,
            rows=blocks,
        )

        docs = gen_documents(people, projects, tasks)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (author:Person {id: row.author_id})
            MERGE (d:Document {id: row.id})
            SET d.title = row.title, d.type = row.type, d.updated_at = row.updated_at
            MERGE (author)-[:AUTHORED]->(d)
            """,
            rows=docs,
        )
        docs_for_project = [d for d in docs if d["target_type"] == "project"]
        docs_for_task = [d for d in docs if d["target_type"] == "task"]
        session.run(
            """
            UNWIND $rows AS row
            MATCH (d:Document {id: row.id}), (proj:Project {id: row.target_id})
            MERGE (d)-[:RELATES_TO]->(proj)
            """,
            rows=docs_for_project,
        )
        session.run(
            """
            UNWIND $rows AS row
            MATCH (d:Document {id: row.id}), (t:Task {id: row.target_id})
            MERGE (d)-[:RELATES_TO]->(t)
            """,
            rows=docs_for_task,
        )

        messages = gen_messages(people, projects, tasks)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (sender:Person {id: row.sender_id}), (proj:Project {id: row.project_id})
            MERGE (m:Message {id: row.id})
            SET m.channel = row.channel, m.text_snippet = row.text_snippet, m.sent_at = row.sent_at
            MERGE (sender)-[:SENT]->(m)
            MERGE (m)-[:IN_CHANNEL_OF]->(proj)
            """,
            rows=messages,
        )
        msg_mentions_person = [m for m in messages if m["mention_type"] == "person"]
        msg_mentions_task = [m for m in messages if m["mention_type"] == "task"]
        session.run(
            """
            UNWIND $rows AS row
            MATCH (m:Message {id: row.id}), (p:Person {id: row.mention_id})
            MERGE (m)-[:MENTIONS]->(p)
            """,
            rows=msg_mentions_person,
        )
        session.run(
            """
            UNWIND $rows AS row
            MATCH (m:Message {id: row.id}), (t:Task {id: row.mention_id})
            MERGE (m)-[:MENTIONS]->(t)
            """,
            rows=msg_mentions_task,
        )

        meetings = gen_meetings(people, projects)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (proj:Project {id: row.project_id})
            MERGE (mt:Meeting {id: row.id})
            SET mt.title = row.title, mt.held_at = row.held_at
            MERGE (mt)-[:ABOUT]->(proj)
            WITH mt, row
            UNWIND row.attendee_ids AS pid
            MATCH (person:Person {id: pid})
            MERGE (person)-[:ATTENDED]->(mt)
            """,
            rows=meetings,
        )

        tools = gen_tools()
        session.run(
            "UNWIND $rows AS row MERGE (t:Tool {id: row.id}) SET t.name = row.name",
            rows=tools,
        )
        project_tools = gen_project_tools(projects, tools)
        session.run(
            """
            UNWIND $rows AS row
            MATCH (proj:Project {id: row.project_id}), (tool:Tool {id: row.tool_id})
            MERGE (proj)-[:USES_TOOL]->(tool)
            """,
            rows=project_tools,
        )

    print(
        f"Seeded: {len(people)} people, {len(teams)} teams, {len(projects)} projects, "
        f"{len(tasks)} tasks, {len(blocks)} blocks, {len(docs)} docs, "
        f"{len(messages)} messages, {len(meetings)} meetings, {len(tools)} tools."
    )
    print(f"\nSample task id for the Context Explorer:  {tasks[0]['id']}")
    print(f"Sample project id for Project Health:      {projects[0]['id']}")
    print(f"Sample person ids for the Path Finder:     {people[0]['id']}, {people[-1]['id']}")


def main():
    if not URI or not PASSWORD:
        raise SystemExit(
            "Missing COGNODB_URI / COGNODB_PASSWORD. Copy .env.example to .env "
            "and fill in your CognoDB Cloud credentials first."
        )
    driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))
    try:
        run(driver)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
