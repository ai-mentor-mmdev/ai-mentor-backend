get_progress_by_account_id = """
SELECT * FROM edu_progress
WHERE account_id = :account_id;
"""

get_topic_by_id = """
SELECT * FROM topics
WHERE id = :id;
"""

get_block_by_id = """
SELECT * FROM blocks
WHERE id = :id;
"""

get_chapter_by_id = """
SELECT * FROM chapters
WHERE id = :id;
"""