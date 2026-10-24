-- ПР7: реляционная модель QueryFlow. Отдельно от служебного db.sqlite3 Django.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'moderator'))
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL CHECK (length(trim(text)) > 0),
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    is_closed INTEGER NOT NULL DEFAULT 0 CHECK (is_closed IN (0, 1)),
    created_on TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL CHECK (length(trim(text)) > 0),
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE RESTRICT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_on TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS questions_category_idx ON questions(category_id);
CREATE INDEX IF NOT EXISTS questions_author_idx ON questions(author_id);
CREATE INDEX IF NOT EXISTS answers_question_idx ON answers(question_id);
CREATE INDEX IF NOT EXISTS answers_author_idx ON answers(author_id);
