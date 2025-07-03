drop_edu_message_table = """
DROP TABLE IF EXISTS edu_messages CASCADE;
"""

drop_edu_chat_table = """
DROP TABLE IF EXISTS edu_chats CASCADE;
"""

drop_chapter_table = """
DROP TABLE IF EXISTS chapters CASCADE;
"""

drop_block_table = """
DROP TABLE IF EXISTS blocks CASCADE;
"""

drop_edu_progress_table = """
DROP TABLE IF EXISTS edu_progress CASCADE;
"""

drop_topic_table = """
DROP TABLE IF EXISTS topics CASCADE;
"""

drop_student_table = """
DROP TABLE IF EXISTS students CASCADE;
"""

# Create tables
create_student_table = """
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_topic_table = """
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    intro TEXT,
    edu_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_block_table = """
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);
"""

create_chapter_table = """
CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    block_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE
);
"""

create_edu_progress_table = """
CREATE TABLE IF NOT EXISTS edu_progress (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    approved_topic_ids INTEGER[] DEFAULT '{}',
    approved_block_ids INTEGER[] DEFAULT '{}',
    approved_chapter_ids INTEGER[] DEFAULT '{}',
    current_topic_id INTEGER,
    current_block_id INTEGER,
    current_chapter_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (current_topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    FOREIGN KEY (current_block_id) REFERENCES blocks(id) ON DELETE SET NULL,
    FOREIGN KEY (current_chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);
"""

create_edu_chat_table = """
CREATE TABLE IF NOT EXISTS edu_chats (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES students(id) ON DELETE CASCADE
);
"""

create_edu_message_table = """
CREATE TABLE IF NOT EXISTS edu_messages (
    id SERIAL PRIMARY KEY,
    edu_chat_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (edu_chat_id) REFERENCES edu_chats(id) ON DELETE CASCADE
);
"""

# Function for automatic updated_at timestamp
create_update_function = """
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';
"""

# Triggers for updated_at
create_student_trigger = """
CREATE TRIGGER update_students_updated_at_trigger
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_topic_trigger = """
CREATE TRIGGER update_topics_updated_at_trigger
BEFORE UPDATE ON topics
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_block_trigger = """
CREATE TRIGGER update_blocks_updated_at_trigger
BEFORE UPDATE ON blocks
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_chapter_trigger = """
CREATE TRIGGER update_chapters_updated_at_trigger
BEFORE UPDATE ON chapters
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_edu_progress_trigger = """
CREATE TRIGGER update_edu_progress_updated_at_trigger
BEFORE UPDATE ON edu_progress
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_edu_chat_trigger = """
CREATE TRIGGER update_edu_chats_updated_at_trigger
BEFORE UPDATE ON edu_chats
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

create_edu_message_trigger = """
CREATE TRIGGER update_edu_messages_updated_at_trigger
BEFORE UPDATE ON edu_messages
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

# Indexes for better performance
create_indexes = """
-- Indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_blocks_topic_id ON blocks(topic_id);
CREATE INDEX IF NOT EXISTS idx_chapters_topic_id ON chapters(topic_id);
CREATE INDEX IF NOT EXISTS idx_chapters_block_id ON chapters(block_id);
CREATE INDEX IF NOT EXISTS idx_edu_progress_account_id ON edu_progress(account_id);
CREATE INDEX IF NOT EXISTS idx_edu_chats_account_id ON edu_chats(account_id);
CREATE INDEX IF NOT EXISTS idx_edu_messages_edu_chat_id ON edu_messages(edu_chat_id);

-- Indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_students_login ON students(login);
CREATE INDEX IF NOT EXISTS idx_edu_progress_current_topic_id ON edu_progress(current_topic_id);
CREATE INDEX IF NOT EXISTS idx_edu_progress_current_block_id ON edu_progress(current_block_id);
CREATE INDEX IF NOT EXISTS idx_edu_progress_current_chapter_id ON edu_progress(current_chapter_id);
"""

# Arrays for easy execution
create_queries = [
    create_student_table,
    create_topic_table,
    create_block_table,
    create_chapter_table,
    create_edu_progress_table,
    create_edu_chat_table,
    create_edu_message_table,
    create_update_function,
    create_student_trigger,
    create_topic_trigger,
    create_block_trigger,
    create_chapter_trigger,
    create_edu_progress_trigger,
    create_edu_chat_trigger,
    create_edu_message_trigger,
    create_indexes
]

drop_queries = [
    drop_edu_message_table,
    drop_edu_chat_table,
    drop_chapter_table,
    drop_block_table,
    drop_edu_progress_table,
    drop_topic_table,
    drop_student_table
]