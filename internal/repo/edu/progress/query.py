# Основные запросы для получения прогресса
get_progress_by_account_id_query = """
SELECT * FROM edu_progress
WHERE account_id = :account_id;
"""

get_progress_by_chat_id_query = """
SELECT ep.* FROM edu_progress ep
JOIN edu_chats ec ON ep.account_id = ec.account_id
WHERE ec.id = :edu_chat_id;
"""

# Запросы для получения текущих ID
get_current_topic_id_query = """
SELECT current_topic_id FROM edu_progress
WHERE account_id = :account_id;
"""

get_current_block_id_query = """
SELECT current_block_id FROM edu_progress
WHERE account_id = :account_id;
"""

get_current_chapter_id_query = """
SELECT current_chapter_id FROM edu_progress
WHERE account_id = :account_id;
"""

# Запросы для получения одобренных ID
get_approved_topic_ids_query = """
SELECT approved_topic_ids FROM edu_progress
WHERE id = :progress_id;
"""

get_approved_block_ids_query = """
SELECT approved_block_ids FROM edu_progress
WHERE id = :progress_id;
"""

get_approved_chapter_ids_query = """
SELECT approved_chapter_ids FROM edu_progress
WHERE id = :progress_id;
"""

# Запросы для обновления текущих позиций
update_current_topic_id_query = """
UPDATE edu_progress
SET current_topic_id = :topic_id
WHERE id = :progress_id;
"""

update_current_block_id_query = """
UPDATE edu_progress
SET current_block_id = :block_id
WHERE id = :progress_id;
"""

update_current_chapter_id_query = """
UPDATE edu_progress
SET current_chapter_id = :chapter_id
WHERE id = :progress_id;
"""

# Запросы для отметки завершения
mark_topic_completed_query = """
UPDATE edu_progress
SET approved_topic_ids = array_append(approved_topic_ids, :topic_id)
WHERE id = :progress_id
AND NOT (:topic_id = ANY(approved_topic_ids));
"""

mark_block_completed_query = """
UPDATE edu_progress
SET approved_block_ids = array_append(approved_block_ids, :block_id)
WHERE account_id = :account_id
AND NOT (:block_id = ANY(approved_block_ids));
"""

mark_chapter_completed_query = """
UPDATE edu_progress
SET approved_chapter_ids = array_append(approved_chapter_ids, :chapter_id)
WHERE account_id = :account_id
AND NOT (:chapter_id = ANY(approved_chapter_ids));
"""

# Запросы для получения объектов (для prompt service)
get_current_topic_query = """
SELECT t.* FROM topics t
JOIN edu_progress ep ON t.id = ep.current_topic_id
WHERE ep.account_id = :account_id;
"""

get_current_block_query = """
SELECT b.* FROM blocks b
JOIN edu_progress ep ON b.id = ep.current_block_id
WHERE ep.account_id = :account_id;
"""

get_current_chapter_query = """
SELECT c.* FROM chapters c
JOIN edu_progress ep ON c.id = ep.current_chapter_id
WHERE ep.account_id = :account_id;
"""

# Запросы для получения доступного контента
get_available_topics_query = """
SELECT * FROM topics
ORDER BY id;
"""

get_available_blocks_query = """
SELECT b.* FROM blocks b
JOIN edu_progress ep ON b.topic_id = ep.current_topic_id
WHERE ep.account_id = :account_id
ORDER BY b.id;
"""

get_available_chapters_query = """
SELECT c.* FROM chapters c
JOIN edu_progress ep ON c.block_id = ep.current_block_id
WHERE ep.account_id = :account_id
ORDER BY c.id;
"""

# Запросы для получения завершенного контента
get_completed_topics_query = """
SELECT t.* FROM topics t
JOIN edu_progress ep ON ep.account_id = :account_id
WHERE t.id = ANY(ep.approved_topic_ids)
ORDER BY t.id;
"""

get_completed_blocks_query = """
SELECT b.* FROM blocks b
JOIN edu_progress ep ON ep.account_id = :account_id
WHERE b.id = ANY(ep.approved_block_ids)
ORDER BY b.id;
"""

get_completed_chapters_query = """
SELECT c.* FROM chapters c
JOIN edu_progress ep ON ep.account_id = :account_id
WHERE c.id = ANY(ep.approved_chapter_ids)
ORDER BY c.id;
"""

# Дополнительные полезные запросы
create_initial_progress_query = """
INSERT INTO edu_progress (account_id, current_topic_id, current_block_id, current_chapter_id)
VALUES (:account_id, :topic_id, NULL, NULL)
RETURNING id;
"""

get_progress_statistics_query = """
SELECT 
    account_id,
    array_length(approved_topic_ids, 1) as completed_topics_count,
    array_length(approved_block_ids, 1) as completed_blocks_count,
    array_length(approved_chapter_ids, 1) as completed_chapters_count,
    current_topic_id,
    current_block_id,
    current_chapter_id,
    created_at,
    updated_at
FROM edu_progress
WHERE account_id = :account_id;
"""

# Запросы для навигации
get_topics_by_name_query = """
SELECT * FROM topics
WHERE LOWER(name) LIKE LOWER(:name_pattern)
ORDER BY id;
"""

get_blocks_by_name_query = """
SELECT b.* FROM blocks b
JOIN edu_progress ep ON b.topic_id = ep.current_topic_id
WHERE ep.account_id = :account_id
AND LOWER(b.name) LIKE LOWER(:name_pattern)
ORDER BY b.id;
"""

get_chapters_by_name_query = """
SELECT c.* FROM chapters c
JOIN edu_progress ep ON c.block_id = ep.current_block_id
WHERE ep.account_id = :account_id
AND LOWER(c.name) LIKE LOWER(:name_pattern)
ORDER BY c.id;
"""

# Запросы для получения контента по ID
get_topic_by_id_query = """
SELECT * FROM topics
WHERE id = :topic_id;
"""

get_block_by_id_query = """
SELECT * FROM blocks
WHERE id = :block_id;
"""

get_chapter_by_id_query = """
SELECT * FROM chapters
WHERE id = :chapter_id;
"""

# Запросы для проверки доступности контента
check_topic_availability_query = """
SELECT EXISTS(
    SELECT 1 FROM topics
    WHERE id = :topic_id
) as is_available;
"""

check_block_availability_query = """
SELECT EXISTS(
    SELECT 1 FROM blocks b
    JOIN edu_progress ep ON b.topic_id = ep.current_topic_id
    WHERE ep.account_id = :account_id
    AND b.id = :block_id
) as is_available;
"""

check_chapter_availability_query = """
SELECT EXISTS(
    SELECT 1 FROM chapters c
    JOIN edu_progress ep ON c.block_id = ep.current_block_id
    WHERE ep.account_id = :account_id
    AND c.id = :chapter_id
) as is_available;
"""

# Запросы для навигации по контенту
navigate_to_topic_query = """
UPDATE edu_progress
SET current_topic_id = :topic_id,
    current_block_id = NULL,
    current_chapter_id = NULL
WHERE account_id = :account_id;
"""

navigate_to_block_query = """
UPDATE edu_progress
SET current_block_id = :block_id,
    current_chapter_id = NULL
WHERE account_id = :account_id;
"""

navigate_to_chapter_query = """
UPDATE edu_progress
SET current_chapter_id = :chapter_id
WHERE account_id = :account_id;
"""

# Запросы для получения прогресса по теме/блоку
get_topic_progress_query = """
SELECT 
    t.id as topic_id,
    t.name as topic_name,
    COUNT(b.id) as total_blocks,
    COUNT(CASE WHEN b.id = ANY(ep.approved_block_ids) THEN 1 END) as completed_blocks,
    (ep.current_topic_id = t.id) as is_current
FROM topics t
LEFT JOIN blocks b ON t.id = b.topic_id
LEFT JOIN edu_progress ep ON ep.account_id = :account_id
WHERE t.id = :topic_id
GROUP BY t.id, t.name, ep.approved_block_ids, ep.current_topic_id;
"""

get_block_progress_query = """
SELECT 
    b.id as block_id,
    b.name as block_name,
    COUNT(c.id) as total_chapters,
    COUNT(CASE WHEN c.id = ANY(ep.approved_chapter_ids) THEN 1 END) as completed_chapters,
    (ep.current_block_id = b.id) as is_current
FROM blocks b
LEFT JOIN chapters c ON b.id = c.block_id
LEFT JOIN edu_progress ep ON ep.account_id = :account_id
WHERE b.id = :block_id
GROUP BY b.id, b.name, ep.approved_chapter_ids, ep.current_block_id;
"""

# Запрос для получения полной структуры курса с прогрессом
get_full_course_structure_query = """
SELECT 
    t.id as topic_id,
    t.name as topic_name,
    t.intro as topic_intro,
    b.id as block_id,
    b.name as block_name,
    c.id as chapter_id,
    c.name as chapter_name,
    (t.id = ANY(ep.approved_topic_ids)) as topic_completed,
    (b.id = ANY(ep.approved_block_ids)) as block_completed,
    (c.id = ANY(ep.approved_chapter_ids)) as chapter_completed,
    (ep.current_topic_id = t.id) as is_current_topic,
    (ep.current_block_id = b.id) as is_current_block,
    (ep.current_chapter_id = c.id) as is_current_chapter
FROM topics t
LEFT JOIN blocks b ON t.id = b.topic_id
LEFT JOIN chapters c ON b.id = c.block_id
LEFT JOIN edu_progress ep ON ep.account_id = :account_id
ORDER BY t.id, b.id, c.id;
"""

# Запросы для удаления и сброса прогресса
reset_progress_query = """
UPDATE edu_progress
SET approved_topic_ids = '{}',
    approved_block_ids = '{}',
    approved_chapter_ids = '{}',
    current_topic_id = NULL,
    current_block_id = NULL,
    current_chapter_id = NULL
WHERE account_id = :account_id;
"""

delete_progress_query = """
DELETE FROM edu_progress
WHERE account_id = :account_id;
"""