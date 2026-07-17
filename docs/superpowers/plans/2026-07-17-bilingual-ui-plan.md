# 三页面中英切换 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent Chinese/English toggle and complete visible UI translation to the home, SP-M, and SP-S standalone pages.

**Architecture:** Keep the three standalone HTML files self-contained. Each page will own a small translation dictionary and the same `gl3dprt-lang` localStorage key, with static nodes marked by `data-i18n` and runtime text produced through a page-local `t()` helper. The device pages will reuse the existing 3D state and only re-render labels after a language change.

**Tech Stack:** Standalone HTML/CSS/JavaScript, existing Three.js module imports, browser localStorage, Playwright smoke verification through the local HTTP server.

## Global Constraints

- Default language is Chinese (`zh`); the toggle target is `EN` in Chinese mode and `中文` in English mode.
- The selected language is stored under `gl3dprt-lang` and shared by all three pages.
- Language changes must not reset geometry, STL state, cuboid state, dimensions, or camera state.
- Keep the existing Camada visual style and all motion-range calculations unchanged.
- Delivery version is `V2.0 · 2026-07-17 · ©Ming Xia` in HTML titles, visible subtitles/meta, and both device docs.
- No external translation library or build step may be added.

### Task 1: Add the shared language behavior to the home page

**Files:**
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/index.html`
- Test: browser smoke checks against `index.html`

**Interfaces:**
- Produces `window.localStorage.gl3dprt-lang` values `zh` or `en`.
- Produces a `#languageToggle` button and updates all `[data-i18n]` nodes on the page.

- [ ] **Step 1: Add a failing DOM smoke assertion**

Use a browser check that expects `#languageToggle`, English heading text after one click, and `localStorage.gl3dprt-lang === "en"`; it must fail before the markup/script exists.

- [ ] **Step 2: Run the assertion and confirm the expected failure**

Run the local page check against `http://127.0.0.1:4294/outputs/index.html`; expected failure is a missing `#languageToggle` or untranslated heading.

- [ ] **Step 3: Implement the home-page toggle**

Add a compact button in `.home-content`, translation markers for eyebrow, heading, description, navigation label, version, and footer, and a page-local dictionary with `readLanguage()`, `t(key)`, `applyLanguage()`, and a click handler. Update `document.documentElement.lang` and `document.title` during `applyLanguage()`.

- [ ] **Step 4: Run the home-page assertion and verify it passes**

Verify default Chinese, one-click English, a second-click Chinese, and persistence in localStorage.

- [ ] **Step 5: Commit the home-page change**

```bash
git add outputs/index.html
git commit -m "feat: add home page language toggle"
```

### Task 2: Add bilingual controls and runtime translations to SP-M and SP-S

**Files:**
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-M.html`
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-S.html`
- Test: browser smoke checks for both device pages

**Interfaces:**
- Each page exposes the same `#languageToggle`, `gl3dprt-lang` storage contract, and `applyLanguage()` behavior.
- Device runtime functions call `t(key, values)` for STL status, model loading status, intersection button, cuboid/model visibility buttons, status HUD, volume, corners, and dimension-unit labels.

- [ ] **Step 1: Add failing device-page assertions**

Check each device page for the toggle, English section titles after clicking, English runtime button text for `Hide Cuboid`/`Show Cuboid`, and an English status/metric label. These checks must fail before translation hooks exist.

- [ ] **Step 2: Run the assertions and confirm they fail for the missing behavior**

Run both pages through the local HTTP server and record the missing toggle/untranslated text as the red test state.

- [ ] **Step 3: Add static translation markers and language controls**

Add the title-area toggle, mark the sidebar headings, STL controls, cuboid controls, view controls, HUD labels, and accessibility labels with translation keys. Keep model-specific explanatory copy separate so SP-M and SP-S can retain their existing wording.

- [ ] **Step 4: Add the shared device translation dictionary and renderer**

Define English and Chinese entries for all marked static labels. `applyLanguage()` updates the HTML language, document title, toggle label/aria-label, view button titles, and current button states without touching Three.js objects.

- [ ] **Step 5: Route all runtime user-facing strings through `t()`**

Replace direct Chinese assignments in the existing handlers/functions for model loading, STL import/clear/intersection, `toggleBox`, `toggleModel`, `updateLabels`, and the initial status. Preserve the existing condition branches and numeric formatting.

- [ ] **Step 6: Run device assertions and verify they pass**

For both SP-M and SP-S, verify Chinese → English → Chinese, persisted language across navigation, no scene reset, correct toggle labels, and no console errors.

- [ ] **Step 7: Commit the device-page change**

```bash
git add outputs/GL-3DPRT-SP-M.html outputs/GL-3DPRT-SP-S.html
git commit -m "feat: localize motion range tools"
```

### Task 3: Update version metadata and usage documentation

**Files:**
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/index.html`
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-M.html`
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-S.html`
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-M说明.md`
- Modify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-S说明.md`

**Interfaces:**
- All user-facing version strings use exactly `V2.0 · 2026-07-17 · ©Ming Xia`.
- Both device documents describe the shared language toggle and persistent language preference.

- [ ] **Step 1: Add a failing metadata check**

Search the three HTML files and two docs for `V1.9`; the check is red while any old version remains.

- [ ] **Step 2: Update all version strings and docs**

Replace old metadata with `V2.0 · 2026-07-17 · ©Ming Xia` and add a concise usage paragraph explaining the `EN`/`中文` button and shared browser preference.

- [ ] **Step 3: Verify metadata and documentation**

Run `rg` to confirm no `V1.9` remains in the five delivery files and the new version appears in each required HTML/document.

- [ ] **Step 4: Commit metadata and docs**

```bash
git add outputs/index.html outputs/GL-3DPRT-SP-M.html outputs/GL-3DPRT-SP-S.html outputs/GL-3DPRT-SP-M说明.md outputs/GL-3DPRT-SP-S说明.md
git commit -m "docs: update bilingual tool version"
```

### Task 4: Full browser verification and delivery

**Files:**
- Verify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/index.html`
- Verify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-M.html`
- Verify: `/Users/ming/Documents/Codex/2026-06-12/new-chat/outputs/GL-3DPRT-SP-S.html`

- [ ] **Step 1: Start the local HTTP server**

Run `python3 -m http.server 4294` from `/Users/ming/Documents/Codex/2026-06-12/new-chat`.

- [ ] **Step 2: Verify all three routes in a desktop browser**

Check page titles, toggle placement, default Chinese labels, English labels, persisted language, sidebar/3D layout, view controls, and absence of horizontal overflow.

- [ ] **Step 3: Verify device interaction regression cases**

On SP-M and SP-S, click `隐藏长方体`/`Hide Cuboid`, confirm cuboid HUD labels disappear and reappear correctly; switch language while hidden; verify the current state label remains accurate. Confirm default geometry and dimensions remain rendered.

- [ ] **Step 4: Check console and source invariants**

Confirm zero page errors, no `V1.9` in delivery files, and both device pages contain a language button and translation dictionary.

- [ ] **Step 5: Push only after fresh verification**

Run `git status --short`, inspect the final diff, then push `main` with the three implementation commits plus the already committed design document.
