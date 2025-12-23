---
id: 004
title: "Image Hover Glow Implementation"
stage: "general"
date: "2025-12-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "king"
command: "/sp.implement"
labels: ["homepage", "ui", "docusaurus", "neon", "glow", "hover"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "src/pages/index.module.css"
tests: []
---

# Image Hover Glow Implementation

## User Input

✨ IMAGE HOVER GLOW — IMPLEMENT PROMPT

(Homepage front image ONLY)

CONTEXT

You are enhancing the front page hero image on the homepage ( / ) of a Docusaurus-based academic textbook website.

This is the main book cover image shown on the left side of the hero section.

🎯 REQUIREMENT

When the user hovers over the book image:

A soft neon glow light should appear from behind the image

Glow should feel like:

futuristic

academic

premium AI textbook

Glow must look like light coming from the background, not a shadow

🎨 VISUAL DETAILS

On hover:

Glow color:

neon cyan / blue

Effect style:

radial glow

soft blur

subtle intensity (not harsh)

Add a very slight scale-up (e.g. micro zoom)

Smooth transition (no sudden jump)

🧱 TECHNICAL RULES

Apply effect only to the front page image

Use pure CSS

No JavaScript

No layout shift

No performance-heavy filters

Glow must NOT cover text or buttons

❌ DO NOT

Do NOT add drop shadow

Do NOT change image itself

Do NOT affect images inside docs pages

Do NOT introduce new elements visually noticeable

✅ FINAL RESULT

Image feels alive and premium

Hover interaction is subtle and elegant

Matches neon / physical-AI theme

Works smoothly on desktop

Implement cleanly without errors.

## Response Summary

Successfully implemented the image hover glow effect for the homepage hero image:

- Applied a soft neon cyan/blue glow effect using multiple layered box-shadows
- Used rgba(63, 224, 255, 0.4) and rgba(63, 224, 255, 0.2) for the glow effect to match the neon theme
- Maintained the existing scale-up effect (scale(1.03)) for the subtle zoom
- Preserved smooth transition and brightness enhancement
- The glow appears as light coming from behind the image, creating a futuristic and premium effect
- Applied only to the homepage hero image using the specific CSS class
- Build successful with no errors