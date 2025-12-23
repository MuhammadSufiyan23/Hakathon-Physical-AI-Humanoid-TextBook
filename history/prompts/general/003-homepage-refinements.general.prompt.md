---
id: 003
title: "Homepage Refinements Implementation"
stage: "general"
date: "2025-12-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "king"
command: "/sp.implement"
labels: ["homepage", "ui", "docusaurus", "academic", "refinement"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "src/pages/index.tsx"
  - "src/pages/index.module.css"
  - "src/css/custom.css"
tests: []
---

# Homepage Refinements Implementation

## User Input

You are making final refinements to the homepage ( / ) of a Docusaurus-based academic textbook website.

Book: Humanoid Robotics & Physical AI
This is NOT a redesign, only improvements and fixes.

1️⃣ CARD SIZE & CONTENT IMPROVEMENT

(Who This Book Is For section)

REQUIRED CHANGES

Increase card width and height noticeably

Cards should feel heavy, premium, textbook-grade

Increase internal padding for readability

CONTENT ENHANCEMENT (add inside each card)
🎓 Students

Add:

Curriculum-aligned learning

Clear mathematical grounding

Concept → application progression

👨‍💻 Developers

Add:

Applied robotics pipelines

Sensor-to-action workflows

Engineering-first explanations

🔬 Researchers

Add:

System-level analysis

Embodied intelligence theory

Physical-world evaluation methods

⚠️ Do NOT remove existing content — only add and enrich

2️⃣ NAVBAR UNDERLINE ISSUE (IMPORTANT FIX)
PROBLEM

Navigation links still show underline / bottom border.

MUST FIX

Remove ALL underline / border-bottom styles from:

"Humanoid Robotics & Physical AI"

"Book Chapters"

"GitHub"

IMPLEMENTATION RULES

Remove underline in:

normal state

hover state

active state

Links must remain clickable

Replace underline with:

soft glow

color transition

NO underline animation

NO border-bottom

This must be fixed via CSS override, not JS.

3️⃣ VISUAL BALANCE CHECK

Cards must align evenly on desktop

No text crowding

Maintain neon + glassmorphism theme

Academic, not flashy

❌ DO NOT

Do NOT change footer

Do NOT modify docs pages

Do NOT change book content

Do NOT add marketing language

Do NOT introduce new sections

✅ FINAL RESULT

Cards feel bigger, richer, more informative

Navbar looks clean and professional

Homepage feels university-level textbook quality

No visual bugs or CSS conflicts

Implement cleanly and safely.

## Response Summary

Successfully implemented all requested homepage refinements:

1. Card Size & Content Improvements:
   - Increased card size with larger padding (2.5rem), height (min-height: 420px), and max-width (400px)
   - Enhanced content for Students card with: Curriculum-aligned learning, Clear mathematical grounding, Concept → application progression
   - Enhanced content for Developers card with: Applied robotics pipelines, Sensor-to-action workflows, Engineering-first explanations
   - Enhanced content for Researchers card with: System-level analysis, Embodied intelligence theory, Physical-world evaluation methods
   - Improved grid layout with better spacing (2.5rem gap)

2. Navbar Underline Fix:
   - Added comprehensive CSS overrides to remove all underline and border-bottom styles
   - Applied fixes to .navbar__link, .navbar__title, .navbar__item, and .navbar__link--active classes
   - Ensured text-decoration: none in all states (normal, hover, active)
   - Maintained soft glow effects as replacement for underlines

3. Visual Balance & Alignment:
   - Ensured cards align evenly on desktop with proper grid layout
   - Added responsive adjustments for different screen sizes
   - Maintained neon + glassmorphism theme throughout
   - Kept academic, professional styling without excessive flashiness

All changes tested and build successful.