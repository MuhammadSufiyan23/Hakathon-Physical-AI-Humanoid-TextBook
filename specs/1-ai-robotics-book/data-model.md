# Data Model: AI-native technical textbook on Physical AI & Humanoid Robotics

## User Entity
- **id**: string (unique identifier)
- **email**: string (user's email, unique)
- **name**: string (user's full name)
- **skill_level**: enum (beginner, intermediate, advanced)
- **programming_experience**: string (user's background in programming)
- **hardware_availability**: string (what robotics hardware the user has access to)
- **created_at**: timestamp (when user account was created)
- **updated_at**: timestamp (when user account was last updated)

## Chapter Entity
- **id**: string (unique identifier)
- **title**: string (title of the chapter)
- **slug**: string (URL-friendly identifier)
- **week_number**: integer (which week this chapter belongs to)
- **content**: string (the markdown content of the chapter)
- **order**: integer (order within the week/chapter sequence)
- **created_at**: timestamp
- **updated_at**: timestamp

## Topic Entity
- **id**: string (unique identifier)
- **chapter_id**: string (foreign key to Chapter)
- **title**: string (title of the topic)
- **content**: string (the markdown content of the topic)
- **order**: integer (order within the chapter)
- **created_at**: timestamp
- **updated_at**: timestamp

## CodeExample Entity
- **id**: string (unique identifier)
- **topic_id**: string (foreign key to Topic)
- **title**: string (title/description of the example)
- **code**: string (the actual code content)
- **language**: enum (python, urdf, launch_xml)
- **description**: string (explanation of what the code does)
- **order**: integer (order within the topic)
- **created_at**: timestamp
- **updated_at**: timestamp

## LabExercise Entity
- **id**: string (unique identifier)
- **week_number**: integer (which week this lab belongs to)
- **title**: string (title of the lab exercise)
- **content**: string (the markdown content with instructions)
- **difficulty**: enum (beginner, intermediate, advanced)
- **estimated_time**: integer (time in minutes to complete)
- **created_at**: timestamp
- **updated_at**: timestamp

## Quiz Entity
- **id**: string (unique identifier)
- **module_id**: string (which module/chapter this quiz belongs to)
- **title**: string (title of the quiz)
- **created_at**: timestamp
- **updated_at**: timestamp

## QuizQuestion Entity
- **id**: string (unique identifier)
- **quiz_id**: string (foreign key to Quiz)
- **question_text**: string (the actual question)
- **question_type**: enum (multiple_choice, true_false, short_answer)
- **order**: integer (order of the question in the quiz)
- **created_at**: timestamp
- **updated_at**: timestamp

## QuizAnswer Entity
- **id**: string (unique identifier)
- **question_id**: string (foreign key to QuizQuestion)
- **answer_text**: string (the answer text)
- **is_correct**: boolean (whether this is the correct answer)
- **explanation**: string (explanation for why this is correct/incorrect)
- **order**: integer (order of the answer option)
- **created_at**: timestamp
- **updated_at**: timestamp

## Progress Entity
- **id**: string (unique identifier)
- **user_id**: string (foreign key to User)
- **chapter_id**: string (foreign key to Chapter)
- **completed**: boolean (whether the chapter is completed)
- **quiz_score**: number (score on the associated quiz if applicable)
- **completed_at**: timestamp (when the chapter was completed)
- **created_at**: timestamp
- **updated_at**: timestamp