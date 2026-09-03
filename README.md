# Hyunseob Baik — research homepage

Phase 3 deployment-ready researcher homepage built with [Quarto](https://quarto.org/) for GitHub Pages.

## Current scope

- English-language site with Home, Research, Publications, Proceedings & Presentations, Projects, CV, and Contact pages
- Responsive navigation and layout
- Local full-text search, social-card metadata, accessible focus states, and a lightweight custom theme
- Verified professional profile, education, appointments, publications, proceedings, selected awards, patents, technology transfer, repository availability, and public contact links
- Structured bibliography in `data/publications.bib` and an optimized profile image derived from the supplied original
- Repository target: [hsbaik/hsbaik.github.io](https://github.com/hsbaik/hsbaik.github.io)
- Least-privilege GitHub Actions workflow for render checks and Pages deployment

English is the confirmed site language. The published baseline is hosted at `https://hsbaik.github.io/`; subsequent design and content changes remain local until they are explicitly reviewed and pushed.

## Local requirements

Install the current stable [Quarto CLI](https://quarto.org/docs/get-started/). No R or Python packages are required for this skeleton.

## Preview and render

From the project directory:

```powershell
quarto preview
```

Build the complete static site:

```powershell
quarto render
```

The rendered output is written to `_site/`. That directory is intentionally ignored by Git.

## Content workflow

1. Resolve the remaining items in `_content/content-todo.yml` using owner-provided or official sources.
2. Keep `data/publications.bib` synchronized with the rendered Publications page.
3. Add media only with descriptive alternative text and confirmed credits or licenses.
4. Render locally and review desktop and mobile layouts.
5. Run the deployment checklist below before adding a publishing workflow.

The `_quarto.yml` `project.render` list is explicit. This keeps planning files, the handoff, and `_content/` out of the generated site.

## Deployment checklist

- Confirm the user-site repository is `hsbaik/hsbaik.github.io` and the default branch is `main`.
- Recheck the confirmed `site-url` and planned `repo-url` in `_quarto.yml`.
- Confirm `robots.txt` and `sitemap.xml` use `https://hsbaik.github.io/`.
- Supply a public-ready 2026 CV PDF and verify any additional 2026 research outputs.
- Resolve every item in `_content/content-todo.yml` and each `TODO(deployment)` marker.
- Check copyright, collaborator consent, sensitive locations, and licenses.
- Run `quarto render`, inspect `_site/`, and test internal links and missing assets.
- Review `.github/workflows/publish.yml`; pull requests render only, while pushes to `main` render and deploy.
- In repository **Settings → Pages**, select **GitHub Actions** as the publishing source only after deployment is approved.
- Confirm the first workflow run succeeds and that `https://hsbaik.github.io/` serves the expected site.

The workflow uses read-only repository access during the build. Only the deploy job receives `pages: write` and `id-token: write`, which are required by GitHub Pages. The action versions follow the current official GitHub Pages guidance, and Quarto is pinned to the locally verified version 1.10.18.

## Authoritative references

- [Quarto websites](https://quarto.org/docs/websites/)
- [Quarto website navigation](https://quarto.org/docs/websites/website-navigation)
- [Publishing to GitHub Pages](https://quarto.org/docs/publishing/github-pages.html)
