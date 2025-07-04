# SQL запросы для работы с чатами

CREATE_CHAT_QUERY = """
INSERT INTO edu_chats (student_id, created_at, updated_at)
VALUES (:student_id, NOW(), NOW())
RETURNING id
"""

GET_CHAT_BY_STUDENT_ID_QUERY = """
SELECT * FROM edu_chats WHERE student_id = :student_id ORDER BY created_at DESC LIMIT 1
"""

CREATE_MESSAGE_QUERY = """
INSERT INTO edu_messages (edu_chat_id, text, role, created_at, updated_at)
VALUES (:chat_id, :text, :role, NOW(), NOW())
RETURNING id
"""

GET_CHAT_HISTORY_QUERY = """
SELECT m.* FROM edu_messages m
JOIN edu_chats c ON m.edu_chat_id = c.id
WHERE c.student_id = :student_id
ORDER BY m.created_at ASC
LIMIT :limit
"""

GET_RECENT_MESSAGES_QUERY = """
SELECT * FROM edu_messages 
WHERE edu_chat_id = :chat_id
ORDER BY created_at DESC
LIMIT :count
"""

CLEAR_CHAT_HISTORY_QUERY = """
DELETE FROM edu_messages 
WHERE edu_chat_id IN (
    SELECT id FROM edu_chats WHERE student_id = :student_id
)
"""

UPDATE_CHAT_TIMESTAMP_QUERY = """
UPDATE edu_chats SET updated_at = NOW() WHERE id = :chat_id
"""

GET_MESSAGES_COUNT_QUERY = """
SELECT COUNT(*) as count FROM edu_messages 
WHERE edu_chat_id = :chat_id
"""