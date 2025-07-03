# internal/repo/edu/topic/query.py

# Запросы для работы с темами (Topics)
create_topic_query = """
INSERT INTO topics (name, intro, edu_plan)
VALUES (:name, :intro, :edu_plan)
RETURNING id;
"""

get_topic_by_id_query = """
SELECT * FROM topics
WHERE id = :topic_id;
"""

get_all_topics_query = """
SELECT * FROM topics
ORDER BY id;
"""

update_topic_query = """
UPDATE topics
SET name = COALESCE(:name, name),
    intro = COALESCE(:intro, intro),
    edu_plan = COALESCE(:edu_plan, edu_plan)
WHERE id = :topic_id;
"""

delete_topic_query = """
DELETE FROM topics
WHERE id = :topic_id;
"""

# Запросы для работы с блоками (Blocks)
create_block_query = """
INSERT INTO blocks (topic_id, name, content)
VALUES (:topic_id, :name, :content)
RETURNING id;
"""

get_block_by_id_query = """
SELECT * FROM blocks
WHERE id = :block_id;
"""

get_blocks_by_topic_id_query = """
SELECT * FROM blocks
WHERE topic_id = :topic_id
ORDER BY id;
"""

update_block_query = """
UPDATE blocks
SET name = COALESCE(:name, name),
    content = COALESCE(:content, content)
WHERE id = :block_id;
"""

delete_block_query = """
DELETE FROM blocks
WHERE id = :block_id;
"""

# Запросы для работы с главами (Chapters)
create_chapter_query = """
INSERT INTO chapters (topic_id, block_id, name, content)
VALUES (:topic_id, :block_id, :name, :content)
RETURNING id;
"""

get_chapter_by_id_query = """
SELECT * FROM chapters
WHERE id = :chapter_id;
"""

get_chapters_by_block_id_query = """
SELECT * FROM chapters
WHERE block_id = :block_id
ORDER BY id;
"""

get_chapters_by_topic_id_query = """
SELECT * FROM chapters
WHERE topic_id = :topic_id
ORDER BY block_id, id;
"""

update_chapter_query = """
UPDATE chapters
SET name = COALESCE(:name, name),
    content = COALESCE(:content, content)
WHERE id = :chapter_id;
"""

delete_chapter_query = """
DELETE FROM chapters
WHERE id = :chapter_id;
"""

# Дополнительные полезные запросы
get_topics_with_stats_query = """
SELECT 
    t.*,
    COUNT(DISTINCT b.id) as blocks_count,
    COUNT(DISTINCT c.id) as chapters_count
FROM topics t
LEFT JOIN blocks b ON t.id = b.topic_id
LEFT JOIN chapters c ON t.id = c.topic_id
GROUP BY t.id, t.name, t.intro, t.edu_plan, t.created_at, t.updated_at
ORDER BY t.id;
"""

get_topic_structure_query = """
SELECT 
    t.id as topic_id,
    t.name as topic_name,
    t.intro as topic_intro,
    t.edu_plan as topic_edu_plan,
    b.id as block_id,
    b.name as block_name,
    c.id as chapter_id,
    c.name as chapter_name
FROM topics t
LEFT JOIN blocks b ON t.id = b.topic_id
LEFT JOIN chapters c ON b.id = c.block_id
WHERE t.id = :topic_id
ORDER BY b.id, c.id;
"""

check_topic_exists_query = """
SELECT EXISTS(
    SELECT 1 FROM topics
    WHERE id = :topic_id
) as exists;
"""

check_block_exists_query = """
SELECT EXISTS(
    SELECT 1 FROM blocks
    WHERE id = :block_id
) as exists;
"""

check_chapter_exists_query = """
SELECT EXISTS(
    SELECT 1 FROM chapters
    WHERE id = :chapter_id
) as exists;
"""