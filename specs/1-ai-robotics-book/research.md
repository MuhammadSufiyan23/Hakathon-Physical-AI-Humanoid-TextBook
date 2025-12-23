# Research: AI-native technical textbook on Physical AI & Humanoid Robotics

## Decision: Docusaurus Version
**Rationale**: Using Docusaurus v2 as specified in user requirements to ensure compatibility with Context7 documentation standards and maintain consistency with existing documentation patterns.
**Alternatives considered**: Docusaurus v3 (newer but potentially less stable), GitBook (different ecosystem), custom React documentation site (more complex to maintain)

## Decision: User Authentication System
**Rationale**: Better-Auth was chosen as specified in user requirements for its simplicity and integration capabilities with modern web applications. Neon database is selected for its serverless PostgreSQL capabilities and ease of use.
**Alternatives considered**: NextAuth.js (more complex for this use case), Auth0 (more enterprise-focused), Firebase Auth (vendor lock-in concerns)

## Decision: Content Structure
**Rationale**: Organizing content in weekly modules as specified in user requirements (13 weeks + additional content) to provide a structured learning path for students. The `/docs/weekly/` and `/docs/physical-ai/` structure follows the user's specified requirements.
**Alternatives considered**: Topic-based structure (less aligned with educational progression), Chapter-based only (missing the weekly progression element)

## Decision: Code Example Format
**Rationale**: Python (ROS2 rclpy), URDF, and .launch XML files as specified in the constitution are the standard formats for the robotics technologies covered in this textbook.
**Alternatives considered**: C++ examples for ROS2 (would complicate consistency as Python is preferred per clarifications), other robot description formats (URDF is the standard for ROS ecosystem)

## Decision: Quiz and Lab Exercise Integration
**Rationale**: Embedding quizzes at the end of each module and providing lab exercises in Markdown format as specified in clarifications ensures consistency with Docusaurus documentation standards while providing interactive learning experiences.
**Alternatives considered**: Separate quiz system (would add complexity), PDF lab exercises (less accessible and harder to maintain)

## Decision: Deployment Strategy
**Rationale**: Vercel or GitHub Pages deployment provides reliable, scalable hosting with good performance characteristics that meet the specified performance goals.
**Alternatives considered**: Self-hosted solutions (more maintenance overhead), Netlify (similar capabilities but Vercel has better Next.js/Docusaurus integration)