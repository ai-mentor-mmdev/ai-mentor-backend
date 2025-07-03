# Запросы для создания чата
create_chat_query = """
INSERT INTO edu_chats (account_id)
VALUES (:account_id)
RETURNING id;
"""

# Запросы для получения чата
get_chat_by_account_id_query = """
SELECT * FROM edu_chats
WHERE account_id = :account_id
ORDER BY created_at DESC
LIMIT 1;
"""

get_chat_by_id_query = """
SELECT * FROM edu_chats
WHERE id = :chat_id;
"""

# Запросы для работы с сообщениями
add_message_query = """
INSERT INTO edu_messages (edu_chat_id, text, role)
VALUES (:edu_chat_id, :text, :role)
RETURNING id;
"""

get_messages_by_chat_id_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
ORDER BY created_at ASC
LIMIT :limit;
"""

get_latest_messages_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
ORDER BY created_at DESC
LIMIT :limit;
"""

get_message_count_query = """
SELECT COUNT(*) as message_count FROM edu_messages
WHERE edu_chat_id = :edu_chat_id;
"""

# Запросы для удаления
delete_all_messages_query = """
DELETE FROM edu_messages
WHERE edu_chat_id = :edu_chat_id;
"""

delete_chat_query = """
DELETE FROM edu_chats
WHERE id = :chat_id;
"""

# Запросы для статистики
get_chat_statistics_query = """
SELECT 
    c.id as chat_id,
    c.account_id,
    c.created_at,
    c.updated_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_time
FROM edu_chats c
LEFT JOIN edu_messages m ON c.id = m.edu_chat_id
WHERE c.account_id = :account_id
GROUP BY c.id, c.account_id, c.created_at, c.updated_at
ORDER BY c.created_at DESC;
"""

get_messages_by_role_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
AND role = :role
ORDER BY created_at ASC;
"""

get_messages_by_date_range_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
AND created_at BETWEEN :start_date AND :end_date
ORDER BY created_at ASC;
"""

# Запросы для поиска в сообщениях
search_messages_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
AND LOWER(text) LIKE LOWER(:search_pattern)
ORDER BY created_at ASC;
"""

# Запрос для получения последнего сообщения
get_last_message_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
ORDER BY created_at DESC
LIMIT 1;
"""

# Запрос для получения первого сообщения
get_first_message_query = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
ORDER BY created_at ASC
LIMIT 1;
"""

# Запросы для обновления сообщений
update_message_query = """
UPDATE edu_messages
SET text = :text
WHERE id = :message_id;
"""

# Запрос для получения всех чатов студента
get_all_chats_by_account_id_query = """
SELECT * FROM edu_chats
WHERE account_id = :account_id
ORDER BY created_at DESC;
"""

# Запрос для получения активных чатов (с сообщениями)
get_active_chats_query = """
SELECT DISTINCT c.* FROM edu_chats c
INNER JOIN edu_messages m ON c.id = m.edu_chat_id
WHERE c.account_id = :account_id
ORDER BY c.updated_at DESC;
"""

# Запрос для получения чатов с количеством сообщений
get_chats_with_message_count_query = """
SELECT 
    c.*,
    COUNT(m.id) as message_count
FROM edu_chats c
LEFT JOIN edu_messages m ON c.id = m.edu_chat_id
WHERE c.account_id = :account_id
GROUP BY c.id, c.account_id, c.created_at, c.updated_at
ORDER BY c.created_at DESC;
"""