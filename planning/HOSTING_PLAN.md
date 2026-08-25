# GitHub Actions and Pages Plan

## Goal

We want to publish a mobile-friendly digest at a GitHub Pages URL while keeping
the existing Python application, GUI, PDF output, and SQLite seen-article
history.

The hosted site will just be a static display of a digest that gets created by an Actions flow that runs on a set timer, thinking once every couple of hours.

## Architecture

GitHub Actions (scheduled)
  -> install the Python project
   -> generate an HTML digest from config/default.yaml
  -> assemble a static Pages site
  -> upload and deploy the Pages artifact

GitHub Pages
  -> serves html, digest HTML, CSS, and JavaScript
  -> stores browser-only seen state in localStorage

The local application remains independent from pages:

Local CLI / GUI
  -> config/config.yaml
  -> SQLite seen_articles.db
  -> PDF or HTML output

## Phase 1: Define the Hosted Content Boundary

1. Publish the Pages site publicly.
2. Use the committed `config/default.yaml` to generate the hosted digest. A
   separate hosted configuration is unnecessary because the repository's feeds,
   categories, and interests are all safe to publish.
3. Continue to exclude `seen_articles.db` and generated local `output/` from
   Git. Neither is required by the Pages deployment.
4. Configure the hosted job to generate HTML only, not PDF. This avoids an
   unnecessary WeasyPrint dependency in the deployment path.
5. Decide retention policy before automation:
   - Publish the current digest at `site/index.html`.
   - Keep dated digests in a browseable archive.
   - Cap the archive at the most recent 30 digests to prevent Pages artifact
     growth.
6. Make `index.html` visually and functionally as close as practical to the
   desktop GUI digest view, while adapting its layout and controls for touch
   screens.

**Acceptance check:** Running the hosted-generation command locally produces a
self-contained directory with an `index.html`, `styles.css`, and `digest.js`.

