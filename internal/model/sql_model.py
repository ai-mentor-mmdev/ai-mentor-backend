# SQL схема базы данных для AI-ментора

# Создание ENUM типов
CREATE_ENUMS = [
    """
    DO $$ BEGIN
        CREATE TYPE programming_experience_enum AS ENUM ('beginner', 'intermediate', 'advanced');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TYPE learning_style_enum AS ENUM ('visual', 'hands-on', 'reading', 'mixed');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TYPE preferred_difficulty_enum AS ENUM ('gradual', 'challenging', 'mixed');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TYPE interview_stage_enum AS ENUM ('WELCOME', 'BACKGROUND', 'GOALS', 'PREFERENCES', 'ASSESSMENT', 'PLAN_GENERATION', 'COMPLETE');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TYPE message_role_enum AS ENUM ('user', 'assistant', 'system');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """
]

# Создание таблиц
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        account_id INTEGER UNIQUE NOT NULL,
        login VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS topics (
        id SERIAL PRIMARY KEY,
        name VARCHAR(500) NOT NULL,
        intro TEXT,
        edu_plan TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS blocks (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
        name VARCHAR(500) NOT NULL,
        content TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS chapters (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
        block_id INTEGER NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
        name VARCHAR(500) NOT NULL,
        content TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        account_id INTEGER UNIQUE NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
        
        -- Состояние интервью
        interview_stage interview_stage_enum DEFAULT 'WELCOME',
        interview_completed BOOLEAN DEFAULT FALSE,
        
        -- Бэкграунд
        programming_experience programming_experience_enum,
        known_languages JSONB DEFAULT '[]',
        work_experience TEXT,
        education_background TEXT,
        
        -- Цели
        learning_goals JSONB DEFAULT '[]',
        career_goals TEXT,
        timeline VARCHAR(100),
        
        -- Предпочтения
        learning_style learning_style_enum,
        time_availability VARCHAR(100),
        preferred_difficulty preferred_difficulty_enum,
        
        -- Адаптация контента
        skip_topics JSONB DEFAULT '{}',
        skip_blocks JSONB DEFAULT '{}',
        focus_areas JSONB DEFAULT '[]',
        recommended_topics JSONB DEFAULT '{}',
        recommended_blocks JSONB DEFAULT '{}',
        
        -- Прогресс
        approved_topics JSONB DEFAULT '{}',
        approved_blocks JSONB DEFAULT '{}',
        approved_chapters JSONB DEFAULT '{}',
        
        -- Оценка уровня
        assessment_score INTEGER CHECK (assessment_score >= 0 AND assessment_score <= 100),
        strong_areas JSONB DEFAULT '[]',
        weak_areas JSONB DEFAULT '[]',
        
        -- Персональный план обучения
        learning_path JSONB DEFAULT '[]',
        current_topic_id INTEGER REFERENCES topics(id),
        current_block_id INTEGER REFERENCES blocks(id),
        current_chapter_id INTEGER REFERENCES chapters(id),
        
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS edu_chats (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS edu_messages (
        id SERIAL PRIMARY KEY,
        edu_chat_id INTEGER NOT NULL REFERENCES edu_chats(id) ON DELETE CASCADE,
        text TEXT NOT NULL,
        role message_role_enum NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
]

# Создание индексов
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_accounts_account_id ON accounts(account_id);",
    "CREATE INDEX IF NOT EXISTS idx_accounts_login ON accounts(login);",

    "CREATE INDEX IF NOT EXISTS idx_students_account_id ON students(account_id);",
    "CREATE INDEX IF NOT EXISTS idx_students_interview_stage ON students(interview_stage);",
    "CREATE INDEX IF NOT EXISTS idx_students_current_topic_id ON students(current_topic_id);",
    "CREATE INDEX IF NOT EXISTS idx_students_current_block_id ON students(current_block_id);",
    "CREATE INDEX IF NOT EXISTS idx_students_current_chapter_id ON students(current_chapter_id);",

    "CREATE INDEX IF NOT EXISTS idx_topics_name ON topics(name);",

    "CREATE INDEX IF NOT EXISTS idx_blocks_topic_id ON blocks(topic_id);",
    "CREATE INDEX IF NOT EXISTS idx_blocks_name ON blocks(name);",

    "CREATE INDEX IF NOT EXISTS idx_chapters_topic_id ON chapters(topic_id);",
    "CREATE INDEX IF NOT EXISTS idx_chapters_block_id ON chapters(block_id);",
    "CREATE INDEX IF NOT EXISTS idx_chapters_name ON chapters(name);",

    "CREATE INDEX IF NOT EXISTS idx_edu_chats_student_id ON edu_chats(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_edu_chats_created_at ON edu_chats(created_at);",

    "CREATE INDEX IF NOT EXISTS idx_edu_messages_chat_id ON edu_messages(edu_chat_id);",
    "CREATE INDEX IF NOT EXISTS idx_edu_messages_role ON edu_messages(role);",
    "CREATE INDEX IF NOT EXISTS idx_edu_messages_created_at ON edu_messages(created_at);"
]

# Создание триггеров для автоматического обновления updated_at
CREATE_TRIGGERS = [
    """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_accounts_updated_at 
            BEFORE UPDATE ON accounts 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_students_updated_at 
            BEFORE UPDATE ON students 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_topics_updated_at 
            BEFORE UPDATE ON topics 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_blocks_updated_at 
            BEFORE UPDATE ON blocks 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_chapters_updated_at 
            BEFORE UPDATE ON chapters 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_edu_chats_updated_at 
            BEFORE UPDATE ON edu_chats 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """,

    """
    DO $$ BEGIN
        CREATE TRIGGER update_edu_messages_updated_at 
            BEFORE UPDATE ON edu_messages 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """
]

# Полный список запросов для создания схемы
create_queries = CREATE_ENUMS + CREATE_TABLES + CREATE_INDEXES + CREATE_TRIGGERS

# Запросы для удаления схемы (в обратном порядке)
DROP_TABLES = [
    "DROP TABLE IF EXISTS edu_messages CASCADE;",
    "DROP TABLE IF EXISTS edu_chats CASCADE;",
    "DROP TABLE IF EXISTS students CASCADE;",
    "DROP TABLE IF EXISTS chapters CASCADE;",
    "DROP TABLE IF EXISTS blocks CASCADE;",
    "DROP TABLE IF EXISTS topics CASCADE;",
    "DROP TABLE IF EXISTS accounts CASCADE;"
]

DROP_ENUMS = [
    "DROP TYPE IF EXISTS message_role_enum CASCADE;",
    "DROP TYPE IF EXISTS interview_stage_enum CASCADE;",
    "DROP TYPE IF EXISTS preferred_difficulty_enum CASCADE;",
    "DROP TYPE IF EXISTS learning_style_enum CASCADE;",
    "DROP TYPE IF EXISTS programming_experience_enum CASCADE;"
]

DROP_FUNCTION = [
    "DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;"
]

# Полный список запросов для удаления схемы
drop_queries = DROP_TABLES + DROP_ENUMS + DROP_FUNCTION

# Тестовые данные для разработки
INSERT_TEST_DATA = [
    """
    INSERT INTO accounts (account_id, login, password) VALUES 
    (1001, 'test_user1', 'hashed_password1'),
    (1002, 'test_user2', 'hashed_password2')
    ON CONFLICT (account_id) DO NOTHING;
    """,

    """
    INSERT INTO topics (name, intro, edu_plan) VALUES 
    ('Основы Python', 'Изучение базовых концепций языка Python', 'Переменные, типы данных, условия, циклы'),
    ('Веб-разработка', 'Создание веб-приложений', 'HTML, CSS, JavaScript, фреймворки'),
    ('Базы данных', 'Работа с базами данных', 'SQL, PostgreSQL, проектирование БД')
    ON CONFLICT DO NOTHING;
    """,

    """
    INSERT INTO blocks (topic_id, name, content) VALUES 
    (1, 'Переменные и типы данных', 'Изучение переменных, чисел, строк, списков'),
    (1, 'Условные конструкции', 'if, elif, else операторы'),
    (1, 'Циклы', 'for и while циклы'),
    (2, 'HTML основы', 'Структура HTML документа'),
    (2, 'CSS стили', 'Стилизация веб-страниц'),
    (3, 'SQL основы', 'SELECT, INSERT, UPDATE, DELETE')
    ON CONFLICT DO NOTHING;
    """,

    """
    INSERT INTO chapters (topic_id, block_id, name, content) VALUES 
    (1, 1, 'Что такое переменная', 'Переменная - это контейнер для хранения данных'),
    (1, 1, 'Типы данных в Python', 'int, float, str, bool, list, dict'),
    (1, 2, 'Условие if', 'Базовая условная конструкция'),
    (1, 2, 'Множественные условия', 'elif и комбинации условий'),
    (2, 4, 'Структура HTML', 'DOCTYPE, html, head, body теги'),
    (3, 6, 'Команда SELECT', 'Выборка данных из таблиц')
    ON CONFLICT DO NOTHING;
    """
]

# Список тестовых запросов
test_data_queries = INSERT_TEST_DATA