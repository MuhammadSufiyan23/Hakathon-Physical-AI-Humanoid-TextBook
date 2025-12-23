---
id: 001
title: "Neon-Tech Dark Theme Implementation"
stage: "general"
date: "2025-12-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "king"
command: "/sp.implement"
labels: ["theme", "css", "docusaurus", "neon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "src/css/custom.css"
tests: []
---

# Neon-Tech Dark Theme Implementation

## User Input

You are working inside a Docusaurus project for a book website called Humanoid Robotics & Physical AI.

🎯 Objective

Implement a professional neon-tech dark theme across the entire book (homepage + docs pages).

⚠️ Critical Rules (Must Follow)

DO NOT change any markdown content or wording

DO NOT remove pages, sections, sidebar items, or footer

Only modify styles (CSS)

No build errors, no runtime errors

Changes must work in both dark & light mode

🔧 IMPLEMENTATION STEPS (DO ALL)
1️⃣ Create / Update File

Work only inside:

src/css/custom.css

If it does not exist, create it.

2️⃣ Define Theme Color Variables

Add CSS variables for a neon-tech palette:

Primary Neon: #3FE0FF

Secondary Neon: #7C7CFF

Accent Purple: #A855F7

Background Dark: #0B0F14

Surface Dark: #111827

Text Main: #E5E7EB

Text Muted: #9CA3AF

3️⃣ Global Styling

Set site background to dark gradient

Improve font contrast and spacing

Smooth transitions for hover effects

4️⃣ Homepage (Front Page)

Implement:

Dark gradient background

Left hero image:

Rounded corners

Neon cyan glow shadow

Hover: scale(1.03) + stronger glow

Right content:

Main heading → neon cyan + soft glow

Subheading → muted gray

"Start Reading" button:

Gradient (cyan → purple)

Hover: glow + slight upward movement

5️⃣ Documentation Pages Styling
Headings

H1:

Color: neon cyan

Glowing underline

H2:

Color: electric blue

H3:

Color: neon purple

Paragraph Text

Color: soft light gray

Increased line-height

6️⃣ Sidebar Styling

Background: dark slate

Active item:

Neon cyan text

Left glowing border

Hover:

Cyan text

Subtle highlight

7️⃣ Table of Contents (Right Panel)

Title: neon cyan

Links:

Default: muted gray

Hover: cyan

Active: cyan + underline

8️⃣ Cards (Homepage Sections)

Dark glassmorphism background

Rounded corners

Neon outline

Hover:

Glow

Slight upward motion

Emojis remain and match neon colors

9️⃣ Footer

Keep structure unchanged

Darker background

Links neon cyan

Hover glow effect

🔍 Final Check

Ensure visual consistency

Ensure no layout breaks

Ensure no content changes

Output:

Only implementation code

No explanations

Ready-to-run CSS

## Response Summary

Successfully implemented a complete neon-tech dark theme for the Docusaurus project. The implementation includes:

- Updated CSS variables with the specified neon-tech color palette
- Global styling with smooth transitions and dark gradient backgrounds
- Homepage hero section with neon glow effects and hover animations
- Documentation page styling with neon-colored headings
- Sidebar styling with active item highlighting
- Table of contents with neon links
- Card styling with glassmorphism effects
- Footer styling with neon links
- All styling works in both dark and light modes

The theme has been tested with a successful build and is running on the development server at http://localhost:3001/.