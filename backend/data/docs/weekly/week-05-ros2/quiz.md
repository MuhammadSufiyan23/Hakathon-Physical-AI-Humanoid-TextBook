---
sidebar_label: 'Week 5 Quiz: Advanced ROS 2 Concepts'
title: 'Week 5 Quiz: Advanced ROS 2 Concepts'
---

# Week 5 Quiz: Advanced ROS 2 Concepts

## Question 1
What does RMW stand for in ROS 2?
- A) Real-time Middleware Workbench
- B) ROS Middleware Interface
- C) Rapid Message Wrapper
- D) Robot Middleware Web

## Question 2
Which DDS implementation is the default in most ROS 2 distributions?
- A) Cyclone DDS
- B) RTI Connext DDS
- C) Fast DDS (formerly Fast RTPS)
- D) OpenDDS

## Question 3
What are the three components of an ROS 2 action?
- A) Request, Response, Update
- B) Goal, Result, Feedback
- C) Command, Status, Progress
- D) Input, Output, State

## Question 4
Which QoS policy determines whether all messages are guaranteed to be delivered?
- A) Durability
- B) History
- C) Reliability
- D) Deadline

## Question 5
What is the default storage format for ROS 2 bags?
- A) .bag (same as ROS 1)
- B) SQLite database
- C) JSON format
- D) XML format

## Question 6
Which command is used to record all topics to a ROS 2 bag?
- A) ros2 record -a
- B) ros2 bag record -a
- C) ros2 bag record --all
- D) ros2 record --all-topics

## Question 7
What is the purpose of the TRANSIENT_LOCAL durability QoS policy?
- A) Only send new messages to subscribers
- B) Send old messages to new subscribers
- C) Store messages on disk
- D) Compress messages

## Question 8
Which middleware configuration allows for real-time critical data transmission?
- A) BEST_EFFORT reliability with VOLATILE durability
- B) RELIABLE reliability with TRANSIENT_LOCAL durability
- C) BEST_EFFORT reliability with TRANSIENT_LOCAL durability
- D) RELIABLE reliability with VOLATILE durability

## Question 9
What is the primary advantage of using actions over services in ROS 2?
- A) Actions are faster than services
- B) Actions can handle long-running operations with feedback and cancellation
- C) Actions don't require a server
- D) Actions use less memory

## Question 10
Which command shows information about a ROS 2 bag file?
- A) ros2 bag show my_bag
- B) ros2 bag info my_bag
- C) ros2 bag inspect my_bag
- D) ros2 bag describe my_bag

## Answer Key
1. B) ROS Middleware Interface
2. C) Fast DDS (formerly Fast RTPS)
3. B) Goal, Result, Feedback
4. C) Reliability
5. B) SQLite database
6. B) ros2 bag record -a
7. B) Send old messages to new subscribers
8. B) RELIABLE reliability with TRANSIENT_LOCAL durability
9. B) Actions can handle long-running operations with feedback and cancellation
10. B) ros2 bag info my_bag