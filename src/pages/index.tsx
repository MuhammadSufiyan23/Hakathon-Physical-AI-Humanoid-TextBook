

import React, {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

import HeroSection from '../components/HeroSection';
import HomepageFeatures from '../components/HomepageFeatures';
import Chatbot from '../components/Chatbot';

/* ================= HERO HEADER ================= */

function HomepageHeader() {
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroImage}>
            <img
              src="/img/Aiimg.jfif"
              alt="Physical AI & Humanoid Robotics Book Cover"
              className={styles.bookCover}
            />
          </div>

          <div className={styles.heroText}>
            <div className={styles.heroTitleContainer}>
              <Heading as="h1" className={clsx("hero__title", styles.heroTitleLine1)}>
                Physical AI & Humanoid
              </Heading>

              <div className={styles.roboticsContainer}>
                <Heading as="h1" className={clsx("hero__title", styles.heroTitleLine2)}>
                  <span className={styles.underlineRobotics}>Robotics</span>
                </Heading>
                <div className={styles.neonDivider}></div>
              </div>
            </div>

            <div className={styles.authorCreditContainer}>
              <span className={styles.authorLine}></span>
              <p className={styles.authorCredit}>
                Created by Muhammad Sufiyan
              </p>
              <span className={styles.authorLine}></span>
            </div>

            <p className="hero__subtitle">
              A modern, in-depth technical textbook exploring AI systems in the physical world and humanoid robotics.
            </p>

            <p className={styles.heroDescription}>
              Designed for students, developers, and researchers,
              this book bridges artificial intelligence with embodied
              robotic systems through structured learning.
            </p>

            <div className={styles.buttons}>
              <Link
                className={`button button--secondary button--lg ${styles.startReadingBtn}`}
                to="/docs/physical-ai/introduction">
                📖 Start Reading
              </Link>
            </div>

          </div>
        </div>
      </div>
    </header>
  );
}

/* ================= SECTIONS ================= */

function WhoThisBookFor() {
  return (
    <section className={styles.section}>
      <div className="container">
        <Heading as="h2" className={styles.sectionTitle}>
          Who This Book Is For
        </Heading>

        <div className={styles.cardsGrid}>
          <div className={clsx(styles.card, styles.cardHover)}>
            <h3 className={styles.cardTitle}>🎓 <span>Students</span></h3>
            <ul className={styles.cardList}>
              <li>Step-by-step foundations</li>
              <li>Structured conceptual learning</li>
              <li>Curriculum-aligned learning</li>
              <li>Concept-to-application clarity</li>
              <li>Beginner-friendly progression</li>
              <li>Hands-on learning approach</li>
              <li>Clear learning milestones</li>

            </ul>
          </div>

          <div className={clsx(styles.card, styles.cardHover)}>
            <h3 className={styles.cardTitle}>👨‍💻 <span>Developers</span></h3>
            <ul className={styles.cardList}>
              <li>Real-world robotics pipelines</li>
              <li>Engineering-first explanations</li>
              <li>Scalable system design</li>
              <li>AI-to-production workflows</li>
              <li>Modular architecture patterns</li>
              <li>Deployment-ready insights</li>
            </ul>
          </div>

          <div className={clsx(styles.card, styles.cardHover)}>
            <h3 className={styles.cardTitle}>🔬 <span>Researchers</span></h3>
            <ul className={styles.cardList}>
              <li>Embodied intelligence research</li>
              <li>Physical-world evaluation</li>
              <li>Experimental insights</li>
              <li>Future research directions</li>
              <li>Benchmark-driven analysis</li>
              <li>Cross-domain perspectives</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function Prerequisites() {
  return (
    <section className={styles.prerequisitesSection}>
      <div className="container">
        <Heading as="h2">Prerequisites</Heading>
        <div className={styles.pillsContainer}>
          <span className={styles.pill}>🧮 Linear Algebra</span>
          <span className={styles.pill}>🐍 Python</span>
          <span className={styles.pill}>🧠 Basic AI</span>
        </div>
      </div>
    </section>
  );
}

function LearningOutcomes() {
  return (
    <section className={styles.outcomesSection}>
      <div className="container">
        <Heading as="h2">What You Will Learn</Heading>
        <ul className={styles.outcomesList}>
          <li>Physical AI foundations</li>
          <li>Humanoid architectures</li>
          <li>Embodied intelligence</li>
        </ul>
      </div>
    </section>
  );
}

/* ================= MAIN HOME (ONLY ONE) ================= */

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();

  return (
    <Layout
      title={siteConfig.title}
      description="AI-native technical textbook on Physical AI and Humanoid Robotics">

      <HomepageHeader />

      <main>
        <HeroSection />
        <HomepageFeatures />
        <WhoThisBookFor />
        <Prerequisites />
        <LearningOutcomes />
      </main>

      {/* Floating RAG Chatbot */}
      {/* <Chatbot /> */}

    </Layout>
  );
}


