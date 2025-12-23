---
id: 002
title: "Homepage Enhancement Implementation"
stage: "general"
date: "2025-12-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "king"
command: "/sp.implement"
labels: ["homepage", "ui", "docusaurus", "academic"]
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

# Homepage Enhancement Implementation

## User Input

You are enhancing ONLY the homepage ( / ) of a Docusaurus-based academic textbook website.

Book: Humanoid Robotics & Physical AI
Audience:

University students

AI engineers

Robotics researchers

The website must feel like:

A flagship university textbook

Academically trusted

Futuristic but highly readable

Structured like a curriculum / syllabus, not a product

🎯 PRIMARY GOAL

Transform the homepage into a professional academic landing page that communicates:

Who the book is for

What background is expected

What readers will learn

While preserving academic seriousness.

✍️ AUTHOR CREDIT (FRONT PAGE ONLY)

In the hero section of the homepage:

Add the text:

Book by Muhammad Sufiyan

Placement

Directly below the main title
"Physical AI & Humanoid Robotics"

Above the description paragraph

Styling

Smaller than the main title

Clean, modern academic typography

Subtle neon cyan / soft gray

No underline

No bold

Slight letter spacing

⚠️ This text must appear ONLY on the homepage, not inside docs pages.

🧱 ADD SECTION — "WHO THIS BOOK IS FOR"
Section Title

Who This Book Is For

Layout

Create 3 large cards:

🎓 Students

Engineering & Computer Science learners

Step-by-step foundations

Structured conceptual learning

👨‍💻 Developers

Practical Physical AI systems

Sensors, control, embodiment

Real-world implementation focus

🔬 Researchers

Cutting-edge humanoid systems

Embodied intelligence research

Physical-world constraints

Design Rules

Glassmorphism cards

Neon border on hover

Subtle vertical lift animation

Professional, not playful

🧱 ADD SECTION — "PREREQUISITES"
Section Title

Prerequisites

Content Style

Use inline pills / tags:

🧮 Linear Algebra

🐍 Python

🧠 Basic AI Concepts

⚙️ Engineering Mindset

Tone:

Welcoming

Academic

Not strict or intimidating

🧱 ADD SECTION — "LEARNING OUTCOMES"
Section Title

What You Will Be Able To Do

Bullet Points

Use check icons:

✅ Understand Physical AI principles

✅ Design embodied intelligent systems

✅ Analyze humanoid robot architectures

✅ Work with sensors and perception

Styling

Neon accent underline under heading

Clean academic spacing

No excessive animations

🎨 ADVANCED VISUAL POLISH

Apply across homepage sections:

Glowing section separators

Slight background shade variation per section

Max content width for readability

Typography

Headings: bold with subtle neon gradient

Paragraphs: soft gray for readability

Emojis: subtle, meaningful, never playful

🔧 NAVBAR LINK CLEANUP (GLOBAL)

In the top navigation bar:

Remove all underline / bottom border effects from:

"Humanoid Robotics & Physical AI"

"Book Chapters"

"GitHub"

Rules:

Links remain fully clickable

Hover effect = soft glow or color shift

No underline animations

❌ DO NOT

Do NOT change book content

Do NOT change docs layout

Do NOT modify footer

Do NOT add pricing, marketing language, or testimonials

Do NOT add new routes

Do NOT introduce errors

This is a textbook, not a product website.

✅ FINAL EXPECTATION

The homepage should read like:

A university syllabus

A research vision

A clear learning journey

Professional, academic, premium textbook-quality.

Implement cleanly.

## Response Summary

Successfully implemented all requested homepage enhancements:

1. Added author credit "Book by Muhammad Sufiyan" in the hero section
2. Created "Who This Book Is For" section with 3 glassmorphism cards
3. Created "Prerequisites" section with pill tags
4. Created "Learning Outcomes" section with check icons
5. Applied visual polish including section separators and background variations
6. Updated navbar link styling to remove underlines
7. All styling follows academic, professional design principles
8. All changes tested and build successful