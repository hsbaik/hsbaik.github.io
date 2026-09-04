# Hyunseob Baik — research homepage

Phase 3 deployment-ready researcher homepage built with [Quarto](https://quarto.org/) for GitHub Pages.

## Current scope

- English-language site with Home, Research, Publications, Proceedings & Presentations, Projects, CV, and Contact pages
- Responsive navigation and layout
- Local full-text search, social-card metadata, accessible focus states, and a lightweight custom theme
- Verified professional profile, education, appointments, publications, proceedings, selected awards, patents, technology transfer, repository availability, and public contact links
- Canonical CV content in `data/cv.json` and an optimized profile image derived from the supplied original
- An automatically generated, downloadable PDF CV built from the same data as the web CV
- Repository target: [hsbaik/hsbaik.github.io](https://github.com/hsbaik/hsbaik.github.io)
- Least-privilege GitHub Actions workflow for render checks and Pages deployment

English is the confirmed site language. The published baseline is hosted at `https://hsbaik.github.io/`; subsequent design and content changes remain local until they are explicitly reviewed and pushed.

## Local requirements

Install the current stable [Quarto CLI](https://quarto.org/docs/get-started/) and Python 3. The CV generator uses only the Python standard library; Quarto supplies the Typst compiler used for the PDF.

## Preview and render

Generate the web CV pages and PDF first:

```powershell
python scripts/build_cv.py --compile
```

Then preview the site from the project directory:

```powershell
quarto preview
```

Build the complete static site:

```powershell
quarto render
```

The rendered output is written to `_site/`. That directory is intentionally ignored by Git.

## Content workflow

1. Edit `data/cv.json` for CV, contact, publication, presentation, patent, technology-transfer, or award updates. The generated `cv.qmd`, `contact.qmd`, `publications.qmd`, `presentations.qmd`, and `patents.qmd` files should not be edited directly.
2. Run `python scripts/build_cv.py --compile` after data changes. This rebuilds the web pages, `output/pdf/Hyunseob_Baik_CV.pdf`, and the site download copy.
3. Add media only with descriptive alternative text and confirmed credits or licenses.
4. Render locally and review desktop and mobile layouts.
5. Run the deployment checklist below before publishing.

The `_quarto.yml` `project.render` list is explicit, so only intended site pages are rendered.

## Deployment checklist

- Confirm the user-site repository is `hsbaik/hsbaik.github.io` and the default branch is `main`.
- Recheck the confirmed `site-url` and planned `repo-url` in `_quarto.yml`.
- Confirm `robots.txt` and `sitemap.xml` use `https://hsbaik.github.io/`.
- Rebuild and review the current PDF CV, and verify any additional 2026 research outputs.
- Check copyright, collaborator consent, sensitive locations, and licenses.
- Run `quarto render`, inspect `_site/`, and test internal links and missing assets.
- Review `.github/workflows/publish.yml`; pull requests render only, while pushes to `main` render and deploy.
- In repository **Settings → Pages**, select **GitHub Actions** as the publishing source only after deployment is approved.
- Confirm the first workflow run succeeds and that `https://hsbaik.github.io/` serves the expected site.

The workflow uses read-only repository access during the build. Only the deploy job receives `pages: write` and `id-token: write`, which are required by GitHub Pages. The action versions follow the current official GitHub Pages guidance, and Quarto is pinned to the locally verified version 1.10.18.

On every pull request and push, the workflow validates `data/cv.json`, regenerates the web CV pages, builds the PDF with Typst, and then renders the Quarto site. Pushes to `main` additionally publish the generated site artifact.

## Authoritative references

- [Quarto websites](https://quarto.org/docs/websites/)
- [Quarto website navigation](https://quarto.org/docs/websites/website-navigation)
- [Publishing to GitHub Pages](https://quarto.org/docs/publishing/github-pages.html)
