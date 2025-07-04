# SQL запросы для работы со студентами

CREATE_STUDENT_QUERY = """
INSERT INTO students (
    account_id, login, password, interview_stage, interview_completed,
    programming_experience, known_languages, work_experience, education_background,
    learning_goals, career_goals, timeline, learning_style, time_availability, preferred_difficulty,
    skip_topics, skip_blocks, focus_areas, recommended_topics, recommended_blocks,
    approved_topics, approved_blocks, approved_chapters, assessment_score, strong_areas, weak_areas,
    learning_path, current_topic_id, current_block_id, current_chapter_id,
    created_at, updated_at
) VALUES (
    :account_id, :login, :password, :interview_stage, :interview_completed,
    :programming_experience, :known_languages, :work_experience, :education_background,
    :learning_goals, :career_goals, :timeline, :learning_style, :time_availability, :preferred_difficulty,
    :skip_topics, :skip_blocks, :focus_areas, :recommended_topics, :recommended_blocks,
    :approved_topics, :approved_blocks, :approved_chapters, :assessment_score, :strong_areas, :weak_areas,
    :learning_path, :current_topic_id, :current_block_id, :current_chapter_id,
    NOW(), NOW()
) RETURNING id
"""

GET_STUDENT_BY_ID_QUERY = """
SELECT * FROM students WHERE id = :student_id
"""

GET_STUDENT_BY_ACCOUNT_ID_QUERY = """
SELECT * FROM students WHERE account_id = :account_id
"""

UPDATE_STUDENT_QUERY = """
UPDATE students SET
    interview_stage = :interview_stage,
    interview_completed = :interview_completed,
    programming_experience = :programming_experience,
    known_languages = :known_languages,
    work_experience = :work_experience,
    education_background = :education_background,
    learning_goals = :learning_goals,
    career_goals = :career_goals,
    timeline = :timeline,
    learning_style = :learning_style,
    time_availability = :time_availability,
    preferred_difficulty = :preferred_difficulty,
    skip_topics = :skip_topics,
    skip_blocks = :skip_blocks,
    focus_areas = :focus_areas,
    recommended_topics = :recommended_topics,
    recommended_blocks = :recommended_blocks,
    approved_topics = :approved_topics,
    approved_blocks = :approved_blocks,
    approved_chapters = :approved_chapters,
    assessment_score = :assessment_score,
    strong_areas = :strong_areas,
    weak_areas = :weak_areas,
    learning_path = :learning_path,
    current_topic_id = :current_topic_id,
    current_block_id = :current_block_id,
    current_chapter_id = :current_chapter_id,
    updated_at = NOW()
WHERE id = :id
"""

UPDATE_PROFILE_FIELDS_QUERY = """
UPDATE students SET
    {fields_to_update},
    updated_at = NOW()
WHERE id = :student_id
"""

SET_INTERVIEW_STAGE_QUERY = """
UPDATE students SET
    interview_stage = :stage,
    updated_at = NOW()
WHERE id = :student_id
"""

SET_INTERVIEW_COMPLETED_QUERY = """
UPDATE students SET
    interview_completed = :completed,
    interview_stage = 'COMPLETE',
    updated_at = NOW()
WHERE id = :student_id
"""

CHECK_INTERVIEW_COMPLETED_QUERY = """
SELECT interview_completed FROM students WHERE id = :student_id
"""