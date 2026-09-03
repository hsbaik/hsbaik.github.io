#!/usr/bin/env python3
"""Generate the web CV pages and a downloadable PDF from data/cv.json."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cv.json"
TYPST_PATH = ROOT / "tmp" / "pdfs" / "Hyunseob_Baik_CV.typ"
PDF_PATH = ROOT / "output" / "pdf" / "Hyunseob_Baik_CV.pdf"
DOWNLOAD_PATH = ROOT / "downloads" / "Hyunseob_Baik_CV.pdf"
SELF_AUTHOR = "Baik, H."
GENERATED_NOTICE = "<!-- Generated from data/cv.json by scripts/build_cv.py. Do not edit directly. -->"


def load_data() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    validate(data)
    return data


def validate(data: dict[str, Any]) -> None:
    required = {
        "person",
        "appointments",
        "education",
        "research_interests",
        "expertise",
        "publications",
        "presentations",
        "patents",
        "technology_transfer",
        "awards",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Missing required top-level keys: {', '.join(missing)}")

    person = data["person"]
    for key in ("name", "title", "department", "institution", "emails", "profiles"):
        if not person.get(key):
            raise ValueError(f"Missing person.{key}")

    ids: set[str] = set()
    for collection in ("publications", "presentations", "patents", "technology_transfer"):
        for item in data[collection]:
            item_id = item.get("id")
            if not item_id:
                raise ValueError(f"An item in {collection} has no id")
            if item_id in ids:
                raise ValueError(f"Duplicate id: {item_id}")
            ids.add(item_id)
            url = item.get("url")
            if url and not url.startswith(("https://", "http://")):
                raise ValueError(f"Unsupported URL for {item_id}: {url}")

    # Privacy guard: these fields are deliberately not part of the public CV.
    forbidden = {"phone", "telephone", "street_address", "home_address"}
    leaked = forbidden.intersection(person)
    if leaked:
        raise ValueError(f"Private contact fields are not allowed: {', '.join(sorted(leaked))}")


def authors_md(authors: list[str]) -> str:
    rendered = [f"**{name}**" if name == SELF_AUTHOR else name for name in authors]
    if len(rendered) == 1:
        return rendered[0]
    if len(rendered) == 2:
        return f"{rendered[0]}, & {rendered[1]}"
    return f"{', '.join(rendered[:-1])}, & {rendered[-1]}"


def link_md(item: dict[str, Any]) -> str:
    if not item.get("url"):
        return ""
    return f" [{item.get('link_label', 'Link')}]({item['url']})"


def tags_md(tags: list[str]) -> str:
    spans = "".join(f'<span class="pub-tag">{tag}</span>' for tag in tags)
    return f'<div class="pub-tags" aria-label="Research topics">{spans}</div>'


def output_entry_md(item: dict[str, Any], *, publication: bool = False) -> str:
    lines = ["::: {.publication-entry}" if publication else "::: {.output-entry}"]
    if item.get("status"):
        lines += [f'<span class="status-label">{item["status"]}</span>', ""]
    if publication:
        authors = authors_md(item["authors"])
        if item.get("details") == "Manuscript under revision":
            citation = (
                f"{authors} ({item['year']}). {item['title']}. "
                f"Manuscript under revision at *{item['venue']}*."
            )
        else:
            detail = f", {item['details']}" if item.get("details") else ""
            citation = (
                f"{authors} ({item['year']}). {item['title']}. "
                f"*{item['venue']}*{detail}.{link_md(item)}"
            )
        lines.append(citation)
    if item.get("tags"):
        lines += ["", tags_md(item["tags"])]
    lines.append(":::")
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def generate_publications(data: dict[str, Any]) -> None:
    person = data["person"]
    entries = "\n\n".join(output_entry_md(item, publication=True) for item in data["publications"])
    profiles = " · ".join(f"[{item['label']}]({item['url']})" for item in person["profiles"] if item["label"] in {"Google Scholar", "ORCID", "ResearchGate"})
    text = f'''---
title: "Publications"
description: "Verified journal articles and manuscripts by Hyunseob Baik."
---

{GENERATED_NOTICE}

Journal articles and manuscripts are listed newest first without year-based sections. Manuscripts still in peer review are clearly labeled and are not presented as published research. **Hyunseob Baik** is highlighted in each entry. Published conference proceedings are listed separately under [Proceedings & Presentations](presentations.qmd).

## Journal articles and manuscripts

{entries}

## Profiles

{profiles}

Citation counts are intentionally omitted because they change over time. The structured CV data are maintained in `data/cv.json`; `data/publications.bib` remains available for citation-oriented workflows.
'''
    write_text(ROOT / "publications.qmd", text)


def generate_presentations(data: dict[str, Any]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    order: list[str] = []
    for item in data["presentations"]:
        category = item["category"]
        if category not in grouped:
            order.append(category)
        grouped[category].append(item)

    sections: list[str] = []
    for category in order:
        entries = "\n\n".join(output_entry_md(item, publication=True) for item in grouped[category])
        sections.append(f"## {category}\n\n{entries}")

    text = f'''---
title: "Proceedings & Presentations"
description: "Conference proceedings and abstracts, invited seminars, and professional contributions by Hyunseob Baik."
---

{GENERATED_NOTICE}

Research outputs are grouped by contribution type and listed newest first within each section. **Hyunseob Baik** is highlighted in each entry. Published identifiers and links are included only when they have been verified.

{chr(10).join(sections)}
'''
    write_text(ROOT / "presentations.qmd", text)


def generate_patents(data: dict[str, Any]) -> None:
    patent_blocks: list[str] = []
    for item in data["patents"]:
        fields = "\n".join(f"- **{label}:** {value}" for label, value in item["fields"])
        note = f"\n\n{item['note']}" if item.get("note") else ""
        patent_blocks.append(
            "\n".join(
                [
                    "::: {.output-entry}",
                    f'<span class="status-label">{item["status"]}</span>',
                    "",
                    f"**{item['title']}**",
                    "",
                    fields,
                    f"- [{item['link_label']}]({item['url']})",
                    "",
                    tags_md(item["tags"]),
                    note.strip(),
                    ":::"
                ]
            ).replace("\n\n\n", "\n\n")
        )

    transfer_blocks = []
    for item in data["technology_transfer"]:
        transfer_blocks.append(
            f'''::: {{.output-entry}}
<span class="status-label">{item["status"]}</span>

**{item["title"]}**

{item["text"]}

[Related project]({item["project_url"]})
:::'''
        )

    text = f'''---
title: "Patents & Technology Transfer"
description: "Verified patents and publicly disclosable technology transfer involving Hyunseob Baik."
---

{GENERATED_NOTICE}

This page records intellectual-property status using official patent records and separates a registered patent from an accepted application. Details not supported by the available records or explicitly approved for public release are omitted.

## Patents

{chr(10).join(patent_blocks)}

## Technology transfer

{chr(10).join(transfer_blocks)}
'''
    write_text(ROOT / "patents.qmd", text)


def generate_cv_page(data: dict[str, Any]) -> None:
    person = data["person"]
    appointments = "\n\n".join(
        f"**{item['role']}** · {item['institution']}<br>\n{item['detail']} · {item['period']}"
        for item in data["appointments"]
    )
    education_parts = []
    for item in data["education"]:
        part = f"**{item['degree']}** · {item['institution']} · {item['year']} · {item['detail']}"
        if item.get("work_title"):
            part += f" · **{item['work_label']}:** *{item['work_title']}*"
        education_parts.append(part)
    education = "\n\n".join(education_parts)
    interests = "\n".join(f"- {item}" for item in data["research_interests"])
    expertise = "\n".join(f"- **{item['label']}:** {item['text']}" for item in data["expertise"])
    awards = "\n".join(f"- {item}" for item in data["awards"])
    patent_summary = "\n\n".join(
        f"**{item['title']}**  \n{item['status']} · "
        + " · ".join(value for label, value in item["fields"] if label in {"Jurisdiction", "Patent number", "Australian application number", "Registration date", "Acceptance date"})
        + f"<br>\n[{item['link_label']}]({item['url']})"
        for item in data["patents"]
    )
    transfer_summary = "\n\n".join(item["text"] for item in data["technology_transfer"])

    text = f'''---
title: "CV"
description: "Web CV and downloadable curriculum vitae for Hyunseob Baik."
---

{GENERATED_NOTICE}

::: {{.cv-intro}}
**{person["name"]}**<br>
{person["title"]}<br>
{person["department"]}<br>
{person["institution"]}
:::

[Download current PDF CV](downloads/Hyunseob_Baik_CV.pdf){{.btn .btn-primary role="button" download="Hyunseob_Baik_CV.pdf"}}

The PDF is generated from the same structured data as this web CV during each site build.

## Appointments

{appointments}

## Education

{education}

## Research interests

{interests}

## Technical expertise

{expertise}

## Patents and technology transfer

See [Patents & Technology Transfer](patents.qmd) for the dedicated research-output record.

{patent_summary}

{transfer_summary}

## Selected awards

{awards}

## Research outputs

See [Publications](publications.qmd), [Proceedings & Presentations](presentations.qmd), [Patents & Technology Transfer](patents.qmd), and [Data & Software Repositories](repositories.qmd). The publication list includes a 2026 manuscript currently under revision at *Icarus*.
'''
    write_text(ROOT / "cv.qmd", text)


def generate_contact(data: dict[str, Any]) -> None:
    person = data["person"]
    emails = "<br>\n".join(f"[{email}](mailto:{email})" for email in person["emails"])
    profiles = "\n".join(f"- [{item['label']}]({item['url']})" for item in person["profiles"])
    text = f'''---
title: "Contact"
description: "Professional contact and researcher-profile links for Hyunseob Baik."
toc: false
---

{GENERATED_NOTICE}

## Professional contact

**{person["name"]}**<br>
{person["title"]}<br>
{person["department"]}<br>
{person["institution"]}

**Email**<br>
{emails}

## Research profiles

{profiles}

Only contact details that the site owner explicitly identified as public are shown here. A street address and phone number are intentionally omitted.
'''
    write_text(ROOT / "contact.qmd", text)


def generate_web(data: dict[str, Any]) -> None:
    generate_publications(data)
    generate_presentations(data)
    generate_patents(data)
    generate_cv_page(data)
    generate_contact(data)


def ts(value: Any) -> str:
    """Return a Typst string literal."""
    return json.dumps(str(value), ensure_ascii=False)


def typst_authors(authors: list[str]) -> str:
    pieces: list[str] = []
    for index, name in enumerate(authors):
        if index:
            pieces.append(" & " if index == len(authors) - 1 else ", ")
        expr = f'#text(weight: "bold", {ts(name)})' if name == SELF_AUTHOR else f"#text({ts(name)})"
        pieces.append(expr)
    return "".join(pieces)


def typst_link(item: dict[str, Any]) -> str:
    if not item.get("url"):
        return ""
    return f' #link({ts(item["url"])})[#text(fill: accent, {ts(item.get("link_label", "Link"))})]'


def typst_output(item: dict[str, Any], number: int) -> str:
    authors = typst_authors(item["authors"])
    status = ""
    if item.get("status"):
        status = f'#status({ts(item["status"])}) #h(4pt)'
    if item.get("details") == "Manuscript under revision":
        ending = f'Manuscript under revision at #emph({ts(item["venue"])}).'
    else:
        detail = f", {item['details']}" if item.get("details") else ""
        ending = f'#emph({ts(item["venue"] + detail)}).{typst_link(item)}'
    content = (
        f"{status}{authors} ({item['year']}). #text({ts(item['title'])}). {ending}"
    )
    return f'''#block(breakable: false, below: 8pt)[
  #grid(columns: (7mm, 1fr), column-gutter: 2mm,
    align(right)[#text(fill: muted, {ts(str(number) + ".")})],
    [{content}]
  )
]'''


def typst_dated(date: str, title: str, institution: str, detail: str, work: str = "") -> str:
    work_segment = f'#text(size: 8.4pt, fill: muted, {ts(" · " + work)})' if work else ""
    return f'''#block(breakable: false, below: 8pt)[
  #grid(columns: (34mm, 1fr), column-gutter: 5mm,
    [#text(size: 8.4pt, fill: muted, {ts(date)})],
    [#text(weight: "bold", {ts(title)}) #text({ts(" · " + institution)})
     #text(size: 8.4pt, fill: muted, {ts(" · " + detail)}){work_segment}]
  )
]'''


def typst_patent(item: dict[str, Any]) -> str:
    fields = "\n".join(
        f'#text(weight: "bold", {ts(label + ":")}) #text({ts(" " + value)})\\'
        for label, value in item["fields"]
    )
    note = f'\n#text(size: 8.2pt, fill: muted, style: "italic", {ts(item["note"])})' if item.get("note") else ""
    return f'''#block(breakable: false, below: 10pt)[
  #status({ts(item["status"])}) #h(4pt) #text(weight: "bold", {ts(item["title"])})\\
  #text(size: 8.5pt)[
    {fields}
    #link({ts(item["url"])})[#text(fill: accent, {ts(item["link_label"])})]
  ]{note}
]'''


def generate_typst(data: dict[str, Any]) -> None:
    person = data["person"]
    profile_lookup = {item["label"]: item["url"] for item in person["profiles"]}
    email_links = " #text(fill: muted, \"·\") ".join(
        f'#link({ts("mailto:" + email)})[#text(fill: accent, {ts(email)})]'
        for email in person["emails"]
    )
    profile_links = " #text(fill: muted, \"·\") ".join(
        f'#link({ts(profile_lookup[label])})[#text(fill: accent, {ts(label)})]'
        for label in ("Google Scholar", "ORCID", "GitHub", "LinkedIn", "ResearchGate") if label in profile_lookup
    )

    appointments = "\n".join(
        typst_dated(item["period"], item["role"], item["institution"], item["detail"])
        for item in data["appointments"]
    )
    education = "\n".join(
        typst_dated(
            item["year"], item["degree"], item["institution"], item["detail"],
            f'{item["work_label"]}: {item["work_title"]}' if item.get("work_title") else ""
        )
        for item in data["education"]
    )
    interests = "\n".join(f'- #text({ts(item)})' for item in data["research_interests"])
    expertise = "\n".join(
        f'- #text(weight: "bold", {ts(item["label"] + ":")}) #text({ts(" " + item["text"])})'
        for item in data["expertise"]
    )
    publications = "\n".join(typst_output(item, index) for index, item in enumerate(data["publications"], 1))

    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_order: list[str] = []
    for item in data["presentations"]:
        if item["category"] not in categories:
            category_order.append(item["category"])
        categories[item["category"]].append(item)
    presentation_sections = []
    presentation_number = 1
    for category in category_order:
        entries = []
        for item in categories[category]:
            entries.append(typst_output(item, presentation_number))
            presentation_number += 1
        presentation_sections.append(f'#subsection({ts(category)})\n' + "\n".join(entries))
    presentations = "\n".join(presentation_sections)
    patents = "\n".join(typst_patent(item) for item in data["patents"])
    transfers = "\n".join(
        f'''#block(breakable: false, below: 10pt)[
  #status({ts(item["status"])}) #h(4pt) #text(weight: "bold", {ts(item["title"])})\\
  #text({ts(item["text"])})
]'''
        for item in data["technology_transfer"]
    )
    awards = "\n".join(f'- #text({ts(item)})' for item in data["awards"])

    typst = f'''// Generated from data/cv.json by scripts/build_cv.py. Do not edit directly.
#let accent = rgb("2f6f91")
#let muted = rgb("626a73")
#set page(
  paper: "a4",
  margin: (x: 18mm, top: 15mm, bottom: 16mm),
  footer: context {{
    align(center)[#text(size: 7.5pt, fill: muted)[Hyunseob Baik #h(5pt) · #h(5pt) #counter(page).display("1")]]
  }}
)
#set text(font: "Libertinus Serif", size: 9.2pt, fill: rgb("171a1d"))
#set par(justify: true, leading: 0.55em)
#set list(indent: 10pt, body-indent: 5pt, spacing: 6pt)
#set document(title: "Hyunseob Baik — Curriculum Vitae", author: "Hyunseob Baik")
#show link: set text(fill: accent)

#let section(title) = {{
  v(11pt)
  text(size: 13pt, weight: "bold", title)
  v(1.5pt)
  line(length: 100%, stroke: 0.7pt + accent)
  v(4pt)
}}

#let subsection(title) = {{
  v(7pt)
  text(size: 10.5pt, weight: "bold", fill: muted, title)
  v(2pt)
}}

#let status(label) = box(
  fill: rgb("e7f0f5"),
  radius: 2pt,
  inset: (x: 4pt, y: 1.5pt),
  text(size: 7.5pt, weight: "bold", fill: accent, label)
)

#grid(
  columns: (1fr, auto),
  align: (left, right),
  [#text(size: 25pt, weight: "bold", {ts(person["name"])})],
  [#text(size: 13pt, fill: muted, {ts("Curriculum Vitae")})]
)
#v(2pt)
#line(length: 100%, stroke: 1pt + accent)
#v(5pt)
#text(weight: "bold", {ts(person["title"])}) #text({ts(" · " + person["department"])})\\
#text({ts(person["institution"])})\\
#text(size: 8.5pt)[{email_links}]\\
#text(size: 8.5pt)[{profile_links}]

#section("Appointments")
{appointments}

#section("Education")
{education}

#section("Research Interests")
{interests}

#section("Technical Expertise")
{expertise}

#pagebreak(weak: true)
#section("Publications")
#text(size: 8.2pt, fill: muted, style: "italic", "Journal articles and manuscripts are listed newest first. Peer-review status is stated explicitly.")
#v(3pt)
{publications}

#section("Proceedings & Presentations")
{presentations}

#section("Patents & Technology Transfer")
#subsection("Patents")
{patents}
#subsection("Technology transfer")
{transfers}

#v(12pt)
#section("Selected Awards")
{awards}
'''
    TYPST_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_text(TYPST_PATH, typst)


def resolve_quarto(cli_value: str | None) -> str:
    candidates = [cli_value, os.environ.get("QUARTO_BIN"), shutil.which("quarto"), shutil.which("quarto.cmd")]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
        if candidate and shutil.which(candidate):
            return str(candidate)
    raise FileNotFoundError("Quarto was not found. Pass --quarto or set QUARTO_BIN.")


def compile_pdf(quarto: str) -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    command = [
        quarto,
        "typst",
        "compile",
        str(TYPST_PATH),
        str(PDF_PATH),
        "--root",
        str(ROOT),
        "--creation-timestamp",
        "1788361200"
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    shutil.copy2(PDF_PATH, DOWNLOAD_PATH)
    print(f"Generated {PDF_PATH.relative_to(ROOT)}")
    print(f"Copied {DOWNLOAD_PATH.relative_to(ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile", action="store_true", help="Compile the Typst source and copy the PDF to downloads/.")
    parser.add_argument("--check", action="store_true", help="Validate data only; do not write generated files.")
    parser.add_argument("--quarto", help="Path to the Quarto executable.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_data()
    if args.check:
        print(f"Validated {DATA_PATH.relative_to(ROOT)}")
        return 0
    generate_web(data)
    generate_typst(data)
    if args.compile:
        compile_pdf(resolve_quarto(args.quarto))
    else:
        print(f"Generated web pages and {TYPST_PATH.relative_to(ROOT)}")
        print("Run again with --compile to build the PDF.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
