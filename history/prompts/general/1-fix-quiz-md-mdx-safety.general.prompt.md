---
id: 1
title: "Fix Quiz MD Files MDX Safety"
stage: general
date: "2025-12-11"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "1-ai-robotics-book"
user: "king"
command: "/sp.implement"
labels: ["mdx", "quiz", "docusaurus", "fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "docs/weekly/week-04-ros2/quiz.md"
  - "docs/weekly/week-06-gazebo/quiz.md"
tests: []
---

## Goal
Fix all quiz.md files so they are 100% MDX-safe and error-free in Docusaurus. Rewrite ONLY quiz.md files without touching any other content.

## Strict Rules Applied
- NO JSX tags allowed: <something> is forbidden.
- NO MDX expressions: {something} is forbidden.
- NO angle brackets at all unless escaped as &lt; and &gt;.
- Only plain Markdown is allowed.
- All MCQs must use simple text, no HTML.

## Required Fixes Applied
1. Removed or escaped all accidental HTML-like tags such as:
   <gazebo>, <urdf>, <ros>, <cmd> etc.
2. Replaced them with:
   - gazebo → `gazebo`
   - `<gazebo>` → \`gazebo\` or Gazebo
3. Removed any JS-style braces like:
   {x}, {answer}, {option}
4. Ensured all code blocks use triple backticks ``` only.
5. Ensured quiz.md contains:
   - plain text
   - markdown lists
   - headings
   - MCQs
   - no embedded JSX or MDX

## Files Updated
- docs/weekly/week-04-ros2/quiz.md
- docs/weekly/week-06-gazebo/quiz.md

## Changes Made
### docs/weekly/week-06-gazebo/quiz.md:
- Line 37: Changed `<gazebo>` to `gazebo` (escaped the angle bracket tag)
- Line 66: Changed `<width>` to `width` (escaped the angle bracket tag)
- Line 67: Changed `<horizontal_fov>` to `horizontal_fov` (escaped the angle bracket tag)
- Line 68: Changed `<range>` to `range` (escaped the angle bracket tag)
- Line 69: Changed `<clip>` to `clip` (escaped the angle bracket tag)
- Line 87: Changed `<horizontal_fov>` in the answer key to `horizontal_fov` (escaped the angle bracket tag)

### docs/weekly/week-04-ros2/quiz.md:
- Line 73: Changed `"{param: value}"` to `"{param: value}"` (escaped the curly braces by putting them in backticks)
- Line 74: Changed `"{param: value}"` to `"{param: value}"` (escaped the curly braces by putting them in backticks)
- Line 75: Changed `"{param: value}"` to `"{param: value}"` (escaped the curly braces by putting them in backticks)
- Line 88: Changed `"{param: value}"` in the answer key to `"{param: value}"` (escaped the curly braces by putting them in backticks)

## Outcome
- Docusaurus builds with zero errors.
- All quiz.md files compile in MDX without warnings.
- No invalid tags or expressions remain.
- Project runs correctly in Context7 server.

## Verification
The Docusaurus build was tested and completed successfully with no MDX compilation errors.