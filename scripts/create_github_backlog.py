#!/usr/bin/env python3
"""One-shot: create M0-M6 milestones, epics, and sub-issues. Idempotent on milestones if titles exist."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

REPO = "Juan-GuevaraBusta/hft-jev"


def gh_json(args: list[str]) -> Any:
    out = subprocess.check_output(["gh", *args], text=True)
    return json.loads(out) if out.strip() else None


def gh_run(args: list[str]) -> str:
    return subprocess.check_output(["gh", *args], text=True).strip()


def list_milestones() -> dict[str, int]:
    data = gh_json(["api", f"repos/{REPO}/milestones", "--paginate"])
    return {m["title"]: m["number"] for m in data}


def ensure_milestone(title: str, description: str) -> int:
    existing = list_milestones()
    if title in existing:
        return existing[title]
    m = gh_json(
        [
            "api",
            f"repos/{REPO}/milestones",
            "-f",
            f"title={title}",
            "-f",
            f"description={description}",
        ]
    )
    return m["number"]


@dataclass
class IssueDef:
    slug: str
    milestone_key: str  # M0..M6
    title: str
    complexity: str
    blocked_by: list[str]
    tipo1: str
    objective: str
    scope_in: str
    scope_out: str
    acceptance: list[str]
    gate_questions: list[str]
    refs: str


EPICS: dict[str, tuple[str, str]] = {
    "M0": (
        "Épica M0: Requisitos y fundamentos",
        "Cerrar debates Tipo 1 (T-101…T-113), plan en 3 entregas, specs 00–06, plantilla ADR y toolchain Python.",
    ),
    "M1": (
        "Épica M1: Corte vertical determinista",
        "Corte vertical sin LLM de pago: dominio, gate, calificación/enrutamiento con broker falso, API mínima, E2E en memoria.",
    ),
    "M2": (
        "Épica M2: Arnés LangGraph y LangSmith",
        "Arnés LangGraph, agentes en 2–3 PRs, OpenRouter por tiers, LangSmith desde el primer run con grafo. Relacionado (no sub-issues): #5–#16 Alpaca.",
    ),
    "M3": (
        "Épica M3: Floci, persistencia, worker e IaC",
        "Compose + Floci (SQS/S3), PostgreSQL, worker, persistencia, IaC sobre Floci, tests de integración.",
    ),
    "M4": (
        "Épica M4: Interfaz vinext",
        "Dashboard Next.js + vinext: evento, artefacto, estados UI. Relacionado: #11 cola de aprobación; broker en #5–#16.",
    ),
    "M5": (
        "Épica M5: Evals y Langfuse",
        "Evaluadores deterministas, datasets/experimentos Langfuse, correlación research_id, reporte local.",
    ),
    "M6": (
        "Épica M6: Entrega",
        "CI, README §17, make demo, docs/cost-model.md, guía onboarding y cierre de limitaciones.",
    ),
}

MILESTONE_TITLES = {
    "M0": "M0 — Requisitos y fundamentos",
    "M1": "M1 — Corte vertical determinista",
    "M2": "M2 — Arnés LangGraph y LangSmith",
    "M3": "M3 — Floci, persistencia, worker e IaC",
    "M4": "M4 — Interfaz vinext",
    "M5": "M5 — Evals y Langfuse",
    "M6": "M6 — Entrega",
}

MILESTONE_DESC = {k: v[1] for k, v in EPICS.items()}


def make_issues() -> list[IssueDef]:
    """Sub-issues from approved roadmap (66 items)."""
    raw: list[dict[str, Any]] = []

    def add(
        slug: str,
        mk: str,
        title: str,
        cx: str,
        blocked: str,
        tipo1: str,
        obj: str,
        scope_in: str,
        scope_out: str,
        acc: list[str],
        gate: list[str],
        refs: str,
    ) -> None:
        raw.append(
            {
                "slug": slug,
                "milestone_key": mk,
                "title": title,
                "complexity": cx,
                "blocked_by": [x.strip() for x in blocked.split(",") if x.strip() and x.strip() != "—"],
                "tipo1": tipo1,
                "objective": obj,
                "scope_in": scope_in,
                "scope_out": scope_out,
                "acceptance": acc,
                "gate_questions": gate,
                "refs": refs,
            }
        )

    # M0
    add(
        "M0-05",
        "M0",
        "Orden aprobado de debates Tipo 1 (Fase A §23.4–5)",
        "M",
        "—",
        "T-101…T-113",
        "Fijar y registrar el orden de debates Tipo 1 antes de implementación sustancial.",
        "Tabla en tasks/backlog.md; mapeo T-101…T-113 (excepto T-111) a PR de debate; aprobación usuario.",
        "Implementación de producto; cierre de debates sin registro.",
        [
            "Orden documentado y aprobado por el usuario",
            "Fila en tradeoffs §3",
            "Sin código de aplicación en el PR",
        ],
        ["¿Por qué este orden y no otro?", "¿Qué debate bloquea el corte vertical?"],
        "master_prompt.md §23.4–5; tasks/backlog.md M0-05",
    )
    debates_m0 = [
        ("M0-T108", "Debate: orquestación LangGraph + prompts/ (ADR-002)", "L", "M0-05", "T-108", "ADR-002, specs/04"),
        ("M0-T109", "Debate: veredictos del gate (PASS/FLAG/BLOCK/NEEDS_DATA)", "M", "M0-T108", "T-109", "§10, tradeoffs T-109"),
        ("M0-T112", "Debate + spike: tiers fast/mid/strong y OpenRouter free", "L", "M0-T109", "T-112, T-001", "ADR-001, desk tiers"),
        ("M0-T113", "Debate: fórmula decision_score, umbrales y límites de riesgo", "L", "M0-T109", "T-113, T-005", "ADR-003 §5.1"),
        ("M0-T105", "Debate: cola SQS + worker vs ejecución más simple (MVP)", "L", "M0-T113", "T-105", "§12"),
        ("M0-T101", "Debate: qué emula Floci vs contenedores propios", "L", "M0-T105", "T-101", "§7.3"),
        ("M0-T102", "Debate: cómputo del worker (contenedor vs Lambda)", "M", "M0-T101", "T-102", "tradeoffs T-102"),
        ("M0-T103", "Debate: Lambda en el MVP", "S", "M0-T102", "T-103", "tradeoffs T-103"),
        ("M0-T104", "Debate: simulación de carga en el MVP", "S", "M0-T103", "T-104", "tradeoffs T-104"),
        ("M0-T106", "Debate: herramienta IaC compatible con Floci", "L", "M0-T101", "T-106", "§7.5"),
        ("M0-T107", "Debate: frontend vinext vs Next estándar y Cloudflare", "M", "M0-T106", "T-107", "§7.4"),
        ("M0-T110", "Debate: turnos 24/7 (night_ingest / morning_desk)", "M", "M0-T108", "T-110", "desk.example.yaml"),
    ]
    for slug, title, cx, blocked, tipo1, refs in debates_m0:
        add(
            slug,
            "M0",
            title,
            cx,
            blocked,
            tipo1,
            f"Cerrar debate Tipo 1 documentado en {refs}.",
            "Rondas §4.3; registro en ADR o tradeoffs; impacto en specs anotado.",
            "Código de producto salvo spike acotado explícito en el issue.",
            [
                "Alternativas ≥3 donde aplique §4.3",
                "Decisión registrada con riesgos",
                "tradeoffs.md actualizado",
            ],
            ["Teach-back del flujo afectado", "¿Qué evidencia reabriría el tema?"],
            f"master_prompt.md §4.3; {refs}",
        )

    add(
        "M0-06",
        "M0",
        "Plan MVP: 3 entregas, roadmap de PRs y brief PR-001",
        "L",
        "M0-T107,M0-T110",
        "—",
        "Documento aprobado de límites MVP y secuencia de PRs.",
        "tasks/milestones.md o backlog; fases B–E; brief PR-001.",
        "Implementación de features.",
        ["Usuario aprueba plan", "PR-001 definido", "Alineado con §8 y §23"],
        ["¿Cuál es el mínimo corte vertical?", "¿Qué se difiere post-MVP?"],
        "master_prompt.md §23.6; M0-06",
    )
    add(
        "M0-08",
        "M0",
        "Plantilla ADR + consolidación decisiones M0",
        "M",
        "M0-06",
        "T-101…T-113",
        "Plantilla ADR y ADRs aceptados para temas cerrados en M0.",
        "ADR-template.md; tablas tradeoffs coherentes.",
        "Nuevos debates sin registro.",
        ["Plantilla usable", "T-111 sustituido por T-005 documentado", "ADRs enlazados desde README"],
        ["¿Qué decisiones siguen abiertas?"],
        "master_prompt.md §4.4; M0-08",
    )
    specs = [
        ("M0-S00", "Spec 00-product-requirements.md", "M0-S08" if False else "M0-08"),
        ("M0-S01", "Spec 01-architecture.md", "M0-S00"),
        ("M0-S02", "Spec 02-domain-model.md", "M0-S01"),
        ("M0-S03", "Spec 03-api-contracts.md", "M0-S02"),
        ("M0-S04", "Spec 04-agent-workflow.md", "M0-S03"),
        ("M0-S05", "Spec 05-verification-and-evaluations.md", "M0-S04"),
        ("M0-S06", "Spec 06-security-and-threat-model.md", "M0-S05"),
    ]
    # fix first spec blocked_by
    specs[0] = ("M0-S00", "Spec 00-product-requirements.md", "M0-08")
    for slug, title, blocked in specs:
        num = title.split()[1].split("-")[0]
        add(
            slug,
            "M0",
            title,
            "M" if slug != "M0-S04" else "L",
            blocked,
            "—",
            f"Redactar y aprobar specs/{title.split()[1]}.",
            "Contenido según master_prompt §6.1 y sección temática.",
            "Implementación en el mismo PR salvo acuerdo explícito.",
            ["Spec versionada en specs/", "Criterios de aceptación del MVP §8", "Revisión tras compuerta"],
            ["Contratos y fallos cubiertos en la spec"],
            f"master_prompt.md §6.1; specs/{title.split()[1]}",
        )

    add(
        "M0-07",
        "M0",
        "Tooling: pyproject.toml, Ruff, pytest, Makefile mínimo",
        "M",
        "M0-S06",
        "—",
        "Toolchain Python y comandos make verificables.",
        "make lint, make test, make test-unit; backend/ esqueleto; .env.example.",
        "Lógica de negocio del grafo.",
        ["Comandos ejecutados con salida real en PR", "Sin secretos en repo"],
        ["¿Qué corre en CI más adelante?"],
        "master_prompt.md §20; M0-07",
    )

    # M1
    m1 = [
        ("M1-T01", "Modelos Pydantic de dominio y ResearchArtifact v1", "M", "M0-07", "T-109", "specs/02"),
        ("M1-T02", "Fixtures de evento y loader de desk.yaml", "S", "M1-T01", "T-112", "config/desk.example.yaml"),
        ("M1-T03", "Recolector de evidencia mock (adaptador identificado)", "M", "M1-T02", "—", "§8 fixtures"),
        ("M1-T04", "Pipeline determinista: validar → clasificar → ensamblar artefacto", "L", "M1-T03", "T-108", "§9 sin grafo"),
        ("M1-T05", "Módulo verificación determinista y veredictos del gate", "L", "M1-T04", "T-109", "§10"),
        (
            "M1-T06",
            "decision_score, límites de riesgo y broker falso",
            "L",
            "M1-T05",
            "T-113, T-005",
            "§5.1; Relacionado #9",
        ),
        ("M1-T07", "FastAPI: salud, enviar evento, estado y artefacto (in-memory)", "M", "M1-T06", "T-105", "§12"),
        ("M1-T08", "Tests E2E deterministas (sin Floci, sin LLM de pago)", "M", "M1-T07", "—", "§19"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m1:
        add(
            slug,
            "M1",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M1: {title}.",
            "Según specs aprobadas y criterios del roadmap M1.",
            "LangGraph; Floci; UI.",
            ["Tests antes que implementación (rojo→verde)", "Comando de verificación en PR", "Sin datos sintéticos sin etiquetar"],
            ["Diseño, contratos, fallos y pruebas críticas"],
            f"master_prompt.md; {refs}",
        )

    m2 = [
        ("M2-T01", "Arnés LangGraph: estado tipado y wiring determinista", "L", "M1-T08", "T-108", "§9"),
        ("M2-T02", "Nodos agente (1/3): Event Analyst + Evidence Researcher", "L", "M2-T01", "T-108, T-112", "prompts/agents"),
        ("M2-T03", "Nodos agente (2/3): Market Impact + Risk and Contradiction", "L", "M2-T02", "T-108", "§9"),
        ("M2-T04", "Nodos agente (3/3): Thesis Synthesizer + publicación artefacto", "L", "M2-T03", "T-108", "thesis_synthesizer.md"),
        ("M2-T05", "Cliente OpenRouter y tiers fail-closed", "M", "M2-T01", "T-112, T-001", "ADR-001"),
        ("M2-T06", "LangSmith: trazas desde el primer run del grafo", "M", "M2-T04,M2-T05", "T-002, T-004", "ADR-001"),
        ("M2-T07", "Dataset dorado mínimo (5–10 casos) para regresión de grafo", "M", "M2-T06", "—", "§11"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m2:
        add(
            slug,
            "M2",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M2: {title}.",
            "Grafo, prompts, observabilidad según spec 04.",
            "Alpaca HTTP (ver issues #5–#16).",
            ["LLM fake en unit tests", "research_id en metadata", "Sin ampliar alcance del PR"],
            ["Flujo del grafo y fallos"],
            f"{refs}; Relacionado Alpaca #5–#16",
        )

    m3 = [
        ("M3-T01", "compose.yaml: PostgreSQL, Floci, red y variables", "M", "M2-T07", "T-101", "§13"),
        ("M3-T02", "Spike verificado: SQS (+DLQ) y S3 contra Floci", "L", "M3-T01", "T-101", "Floci"),
        ("M3-T03", "Persistencia PostgreSQL (SQLAlchemy + Alembic)", "L", "M3-T01", "T-101", "§7.3"),
        ("M3-T04", "API: encolar job SQS, idempotencia y estados", "L", "M3-T02,M3-T03", "T-105", "§12"),
        ("M3-T05", "Worker consumidor SQS ejecuta grafo LangGraph", "L", "M3-T04,M2-T06", "T-102", "worker"),
        ("M3-T06", "Persistencia artefacto en S3 (Floci) + lectura API", "M", "M3-T05", "T-101", "S3"),
        ("M3-T07", "IaC: recursos diseño AWS desplegados en Floci", "L", "M3-T02", "T-106", "make infra-up"),
        ("M3-T08", "Suite integración Floci (PG + SQS + S3)", "L", "M3-T06,M3-T07", "T-101, T-105", "§19"),
        ("M3-T09", "Documento docs/aws-vs-floci.md y operaciones", "S", "M3-T08", "T-101", "§17"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m3:
        add(
            slug,
            "M3",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M3: {title}.",
            "Integración local Floci; sin AWS real.",
            "Frontend.",
            ["make test-integration donde aplique", "Gaps Floci documentados"],
            ["Idempotencia y caída de worker"],
            refs,
        )

    m4 = [
        ("M4-T01", "Bootstrap frontend Next.js + vinext (TypeScript)", "M", "M3-T04,M0-T107", "T-107", "§7.4"),
        ("M4-T02", "UI: enviar evento y seguimiento de estado del run", "M", "M4-T01", "—", "§7.4 estados"),
        ("M4-T03", "UI: visor de artefacto (fuentes, escenarios, riesgos, verificación)", "L", "M4-T02", "T-109", "§9"),
        ("M4-T04", "UI: cola de aprobación de órdenes (awaiting_approval)", "M", "M4-T03,M1-T06", "T-113", "Relacionado #11"),
        ("M4-T05", "Tests E2E frontend del recorrido principal", "M", "M4-T04", "—", "§19 frontend"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m4:
        add(
            slug,
            "M4",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M4: {title}.",
            "Dashboard local; API backend existente.",
            "Claves Alpaca en cliente.",
            ["Estados loading/empty/error/done", "Render seguro"],
            ["Recorrido principal demo"],
            refs,
        )

    m5 = [
        ("M5-T01", "Evaluadores deterministas (esquema, citas, reintentos)", "L", "M2-T07", "T-109", "§11"),
        ("M5-T02", "Integración Langfuse: datasets y experimentos", "L", "M5-T01", "T-003", "ADR-001"),
        ("M5-T03", "Correlación research_id LangSmith ↔ Langfuse", "M", "M5-T02,M2-T06", "T-002, T-003", "§15"),
        ("M5-T04", "DecisionEvaluator + adaptador Jev (mock)", "M", "M5-T01", "—", "§11 Jev"),
        ("M5-T05", "Comando make eval y reporte local reproducible", "M", "M5-T02", "—", "§11"),
        ("M5-T06", "Dataset curado 15–30 casos y umbrales documentados", "L", "M5-T05", "T-113", "§11"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m5:
        add(
            slug,
            "M5",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M5: {title}.",
            "evaluations/; Langfuse cloud según ADR-001.",
            "Bloquear CI con evals costosos.",
            ["Reporte local + Langfuse", "Mocks en unit"],
            ["Qué establece cada evaluador"],
            refs,
        )

    m6 = [
        ("M6-T01", "GitHub Actions: lint, tipos, unit, build frontend", "M", "M5-T06,M4-T05", "—", "§19 CI"),
        ("M6-T02", "Endurecimiento seguridad API (rate limit, validación, 429)", "M", "M3-T04", "T-005", "OWASP"),
        ("M6-T03", "README §17: arquitectura AWS, Floci, LangGraph, observabilidad", "L", "M3-T09,M5-T03", "T-101, T-107", "§17"),
        ("M6-T04", "docs/getting-started.md y Makefile §20 completos", "M", "M6-T03", "—", "§20"),
        ("M6-T05", "make demo reproducible (fixtures; paper Alpaca opcional)", "L", "M6-T04,M3-T08", "T-005", "§21"),
        ("M6-T06", "docs/cost-model.md (estimación AWS no incurrida)", "S", "M6-T03", "—", "§13"),
        ("M6-T07", "Cierre backlog: limitaciones, tareas restantes, CONTRIBUTING", "S", "M6-T05", "—", "tasks/backlog.md"),
    ]
    for slug, title, cx, blocked, tipo1, refs in m6:
        add(
            slug,
            "M6",
            title,
            cx,
            blocked,
            tipo1,
            f"Incremento M6: {title}.",
            "Entrega y documentación verificable.",
            "Nuevas features fuera MVP.",
            ["Comandos reales en PR", "Checklist §21"],
            ["Demo ante jurado"],
            refs,
        )

    return [IssueDef(**r) for r in raw]


def format_body(issue: IssueDef, slug_to_num: dict[str, int]) -> str:
    deps = issue.blocked_by
    dep_lines = []
    for s in deps:
        if s in slug_to_num:
            dep_lines.append(f"- Bloqueado por #{slug_to_num[s]} (`{s}`)")
        else:
            dep_lines.append(f"- Bloqueado por `{s}` (pendiente de número)")
    if not dep_lines:
        dep_lines.append("- Ninguna")

    acc = "\n".join(f"- {a}" for a in issue.acceptance)
    gate = "\n".join(f"- {q}" for q in issue.gate_questions)

    return f"""## Objetivo
{issue.objective}

## Alcance
**Incluye:** {issue.scope_in}

**NO incluye:** {issue.scope_out}

## Dependencias
{chr(10).join(dep_lines)}

## Decisiones Tipo 1
{issue.tipo1}

## Criterios de aceptación
{acc}

## Preguntas críticas de la compuerta
{gate}

**Complejidad:** {issue.complexity}

**Referencias:** {issue.refs}

---
`slug_id`: `{issue.slug}`
"""


def create_issue(title: str, body: str, milestone_title: str) -> int:
    path = subprocess.check_output(["mktemp"], text=True).strip()
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    out = gh_run(
        [
            "issue",
            "create",
            "--repo",
            REPO,
            "--title",
            title,
            "--body-file",
            path,
            "--label",
            "feature",
            "--milestone",
            milestone_title,
        ]
    )
    m = re.search(r"/issues/(\d+)", out)
    if not m:
        raise RuntimeError(f"Could not parse issue number from: {out}")
    return int(m.group(1))


def link_sub_issue(parent: int, child: int) -> bool:
    try:
        gh_run(
            [
                "api",
                f"repos/{REPO}/issues/{parent}/sub_issues",
                "-F",
                f"sub_issue_id={child}",
            ]
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> None:
    if "--dry-run" in sys.argv:
        issues = make_issues()
        print(f"Would create {len(issues)} sub-issues + 7 epics + 7 milestones")
        return

    milestone_nums: dict[str, int] = {}
    for key, title in MILESTONE_TITLES.items():
        milestone_nums[key] = ensure_milestone(title, MILESTONE_DESC[key])
        print(f"Milestone {title} -> #{milestone_nums[key]}")

    epic_nums: dict[str, int] = {}
    for key, (etitle, edesc) in EPICS.items():
        body = f"""## Objetivo
Épica del milestone {MILESTONE_TITLES[key]}.

## Alcance
{edesc}

## Sub-issues
Se enlazan automáticamente como sub-issues de este issue.

**Complejidad:** L (contenedor)

`slug_id`: `EPIC-{key}`
"""
        num = create_issue(etitle, body, MILESTONE_TITLES[key])
        epic_nums[key] = num
        print(f"Epic {key} -> #{num}")

    slug_to_num: dict[str, int] = dict(epic_nums)
    issues = make_issues()
    sub_by_milestone: dict[str, list[int]] = {k: [] for k in EPICS}

    for issue in issues:
        body = format_body(issue, slug_to_num)
        num = create_issue(issue.title, body, MILESTONE_TITLES[issue.milestone_key])
        slug_to_num[issue.slug] = num
        sub_by_milestone[issue.milestone_key].append(num)
        print(f"  {issue.slug} -> #{num}")

    linked = 0
    for key, epic_num in epic_nums.items():
        for child in sub_by_milestone[key]:
            if link_sub_issue(epic_num, child):
                linked += 1
        # refresh body with checklist fallback
        children = sub_by_milestone[key]
        checklist = "\n".join(f"- [ ] #{n}" for n in children)
        epic_body = gh_run(["issue", "view", str(epic_num), "--repo", REPO, "--json", "body", "-q", ".body"])
        if "## Checklist sub-issues" not in epic_body:
            new_body = epic_body + f"\n\n## Checklist sub-issues\n{checklist}\n"
            path = subprocess.check_output(["mktemp"], text=True).strip()
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_body)
            gh_run(["issue", "edit", str(epic_num), "--repo", REPO, "--body-file", path])

    # Second pass: update bodies with final dependency numbers
    for issue in issues:
        num = slug_to_num[issue.slug]
        body = format_body(issue, slug_to_num)
        path = subprocess.check_output(["mktemp"], text=True).strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        gh_run(["issue", "edit", str(num), "--repo", REPO, "--body-file", path])

    manifest = {
        "milestones": milestone_nums,
        "epics": epic_nums,
        "issues": {s: slug_to_num[s] for s in sorted(slug_to_num) if s.startswith(("M0", "M1", "M2", "M3", "M4", "M5", "M6", "EPIC"))},
    }
    manifest_path = "/Users/juanluisguevarabustamante/Developer/personal/hft-jev/tasks/github-backlog-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"Linked sub-issues via API: {linked}/{sum(len(v) for v in sub_by_milestone.values())}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
