import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: [
        'physical-ai/introduction',
        'physical-ai/glossary',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 1: Physical AI Foundations',
      items: [
        'weekly/week-01-physical-ai/foundations',
        'weekly/week-01-physical-ai/digital-ai-physical-laws',
        'weekly/week-01-physical-ai/humanoid-robotics-landscape',
        'weekly/week-01-physical-ai/sensor-systems',
        'weekly/week-01-physical-ai/quiz',
        'weekly/week-01-physical-ai/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 2: Embodied Intelligence',
      items: [
        'weekly/week-02-physical-ai/embodied-intelligence',
        'weekly/week-02-physical-ai/overview-applications',
        'weekly/week-02-physical-ai/quiz',
        'weekly/week-02-physical-ai/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 3: ROS 2 Fundamentals - Core Concepts',
      items: [
        'weekly/week-03-ros2/introduction',
        'weekly/week-03-ros2/nodes-topics-services',
        'weekly/week-03-ros2/packages-workspaces',
        'weekly/week-03-ros2/quiz',
        'weekly/week-03-ros2/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 4: ROS 2 Fundamentals - Development',
      items: [
        'weekly/week-04-ros2/client-libraries',
        'weekly/week-04-ros2/launch-files',
        'weekly/week-04-ros2/testing-debugging',
        'weekly/week-04-ros2/quiz',
        'weekly/week-04-ros2/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 5: ROS 2 Fundamentals - Advanced Topics',
      items: [
        'weekly/week-05-ros2/ros2-packages',
        'weekly/week-05-ros2/rosbags-actions',
        'weekly/week-05-ros2/middleware-transport',
        'weekly/week-05-ros2/quiz',
        'weekly/week-05-ros2/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 6: Robot Simulation with Gazebo',
      items: [
        'weekly/week-06-gazebo/introduction',
        'weekly/week-06-gazebo/world-modeling',
        'weekly/week-06-gazebo/robot-modeling',
        'weekly/week-06-gazebo/sensors-plugins',
        'weekly/week-06-gazebo/quiz',
        'weekly/week-06-gazebo/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 7: Robot Simulation - Advanced Modeling',
      items: [
        'weekly/week-07-gazebo/physics-engines',
        'weekly/week-07-gazebo/simulation-environments',
        'weekly/week-07-gazebo/integration-ros2',
        'weekly/week-07-gazebo/quiz',
        'weekly/week-07-gazebo/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 8: NVIDIA Isaac Platform - Introduction',
      items: [
        'weekly/week-08-isaac/introduction',
        'weekly/week-08-isaac/isaac-sdk',
        'weekly/week-08-isaac/carter-robot',
        'weekly/week-08-isaac/quiz',
        'weekly/week-08-isaac/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 9: NVIDIA Isaac Platform - AI Capabilities',
      items: [
        'weekly/week-09-isaac/perception-pipelines',
        'weekly/week-09-isaac/ai-models',
        'weekly/week-09-isaac/computer-vision',
        'weekly/week-09-isaac/quiz',
        'weekly/week-09-isaac/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 10: NVIDIA Isaac Platform - Advanced AI',
      items: [
        'weekly/week-10-isaac/navigation',
        'weekly/week-10-isaac/manipulation',
        'weekly/week-10-isaac/simulation-workflows',
        'weekly/week-10-isaac/quiz',
        'weekly/week-10-isaac/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 11: Humanoid Robot Development - Kinematics',
      items: [
        'weekly/week-11-humanoid/introduction',
        'weekly/week-11-humanoid/kinematics',
        'weekly/week-11-humanoid/dynamics',
        'weekly/week-11-humanoid/quiz',
        'weekly/week-11-humanoid/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 12: Humanoid Robot Development - Interaction',
      items: [
        'weekly/week-12-humanoid/bipedal-locomotion',
        'weekly/week-12-humanoid/human-robot-interaction',
        'weekly/week-12-humanoid/control-systems',
        'weekly/week-12-humanoid/quiz',
        'weekly/week-12-humanoid/lab-exercise',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Week 13: Conversational Robotics',
      items: [
        'weekly/week-13-conversational/introduction',
        'weekly/week-13-conversational/natural-language-processing',
        'weekly/week-13-conversational/dialogue-systems',
      ],
      collapsed: false,
    },
  ],
};

export default sidebars;
