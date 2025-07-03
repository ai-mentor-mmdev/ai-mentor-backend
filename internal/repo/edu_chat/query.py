create_edu_chat = """
INSERT INTO edu_chats (account_id)
VALUES (:account_id)
RETURNING id;
"""

get_edu_chat_by_account_id = """
SELECT * FROM edu_chats
WHERE account_id = :account_id;
"""

create_edu_message = """
INSERT INTO edu_messages (edu_chat_id, text, role)
VALUES (:edu_chat_id, :text, :role)
RETURNING id;
"""

get_edu_messages_by_chat_id = """
SELECT * FROM edu_messages
WHERE edu_chat_id = :edu_chat_id
ORDER BY created_at ASC;
"""