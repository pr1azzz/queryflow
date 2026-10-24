-- ПР7. Каждый именованный запрос реально используется страницами QueryFlow.
-- Значения для ? передаются отдельно через execute(sql, parameters).

-- name: category_list
-- 01. Выборка списка категорий: /categories/ и форма поиска.
SELECT id, name, is_active FROM categories ORDER BY name COLLATE NOCASE, id;

-- name: user_list
-- 02. Выборка участников: страница статистики.
SELECT id, name, role FROM users ORDER BY name COLLATE NOCASE, id;

-- name: active_categories
-- 03. WHERE: только доступные категории /categories/active/.
SELECT id, name, is_active FROM categories
WHERE is_active = 1 ORDER BY name COLLATE NOCASE, id;

-- name: open_questions
-- 04. WHERE: незакрытые вопросы /questions/open/.
SELECT q.*, c.name AS category_name, u.name AS author_name,
       (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) AS answers_count
FROM questions q
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = q.author_id
WHERE q.is_closed = 0
ORDER BY q.created_on DESC, q.id DESC;

-- name: question_list
-- 05. JOIN: вопросы, категории и авторы /questions/.
SELECT q.*, c.name AS category_name, u.name AS author_name,
       (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) AS answers_count
FROM questions q
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = q.author_id
ORDER BY q.created_on DESC, q.id DESC;

-- name: answer_list
-- 06. JOIN четырёх таблиц: ответы, вопрос, категория и автор /answers/.
SELECT a.*, q.text AS question_text, c.name AS category_name,
       u.name AS author_name
FROM answers a
JOIN questions q ON q.id = a.question_id
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = a.author_id
ORDER BY a.created_on DESC, a.id DESC;

-- name: question_summary
-- 07. Агрегаты COUNT/SUM: итоги вопросов на странице статистики.
SELECT COUNT(*) AS total,
       COALESCE(SUM(CASE WHEN is_closed = 0 THEN 1 ELSE 0 END), 0) AS open_count,
       COALESCE(SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END), 0) AS closed_count
FROM questions;

-- name: answer_summary
-- 08. Агрегаты COUNT и COUNT DISTINCT: ответы и число ответивших участников.
SELECT COUNT(*) AS total, COUNT(DISTINCT author_id) AS authors_count FROM answers;

-- name: category_statistics
-- 09. LEFT JOIN + GROUP BY + HAVING: число вопросов по категориям.
-- Параметр: минимальное число вопросов. При 0 видны и пустые категории.
SELECT c.id, c.name, COUNT(q.id) AS questions_count
FROM categories c LEFT JOIN questions q ON q.category_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(q.id) >= ?
ORDER BY questions_count DESC, c.id;

-- name: author_statistics
-- 10. Вторая группировка: количество ответов каждого пользователя, включая 0.
SELECT u.id, u.name, COUNT(a.id) AS answers_count
FROM users u LEFT JOIN answers a ON a.author_id = u.id
GROUP BY u.id, u.name
ORDER BY answers_count DESC, u.id;

-- name: question_search
-- 11. Параметризованный поиск: текст, категория, начальная дата, LIMIT/OFFSET.
-- lower() SQLite игнорирует регистр ASCII; для кириллицы регистр учитывается.
-- Параметры: текст дважды, категория дважды (NULL = любая), дата дважды,
-- размер страницы, сдвиг. instr() ищет буквальную подстроку, не SQL-шаблон.
SELECT q.*, c.name AS category_name, u.name AS author_name,
       (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) AS answers_count
FROM questions q
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = q.author_id
WHERE (? = '' OR instr(lower(q.text), lower(?)) > 0)
  AND (? IS NULL OR q.category_id = ?)
  AND (? = '' OR q.created_on >= ?)
ORDER BY q.created_on DESC, q.id DESC
LIMIT ? OFFSET ?;

-- name: search_count
-- 12. Число найденных вопросов до разбиения на страницы (те же 6 параметров).
SELECT COUNT(*) AS total FROM questions q
WHERE (? = '' OR instr(lower(q.text), lower(?)) > 0)
  AND (? IS NULL OR q.category_id = ?)
  AND (? = '' OR q.created_on >= ?);

-- name: question_detail
-- 13. Карточка вопроса: параметр question_id.
SELECT q.*, c.name AS category_name, u.name AS author_name,
       (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) AS answers_count
FROM questions q
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = q.author_id
WHERE q.id = ?;

-- name: question_answers
-- 14. Ответы на выбранный вопрос: параметр question_id.
SELECT a.*, q.text AS question_text, u.name AS author_name
FROM answers a
JOIN questions q ON q.id = a.question_id
JOIN users u ON u.id = a.author_id
WHERE a.question_id = ? ORDER BY a.created_on, a.id;

-- name: category_detail
-- 15. Карточка категории: параметр category_id.
SELECT id, name, is_active FROM categories WHERE id = ?;

-- name: category_questions
-- 16. Вопросы категории: параметр category_id.
SELECT id, text, created_on, is_closed FROM questions
WHERE category_id = ? ORDER BY created_on DESC, id DESC;

-- name: answer_detail
-- 17. Карточка ответа с данными вопроса, категории и автора: параметр answer_id.
SELECT a.*, q.text AS question_text, c.name AS category_name,
       u.name AS author_name
FROM answers a
JOIN questions q ON q.id = a.question_id
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = a.author_id
WHERE a.id = ?;

-- name: unanswered_questions
-- 18. Дополнительный сценарий: открытые вопросы без ответов (NOT EXISTS).
SELECT q.*, c.name AS category_name, u.name AS author_name, 0 AS answers_count
FROM questions q
JOIN categories c ON c.id = q.category_id
JOIN users u ON u.id = q.author_id
WHERE q.is_closed = 0
  AND NOT EXISTS (SELECT 1 FROM answers a WHERE a.question_id = q.id)
ORDER BY q.created_on DESC, q.id DESC;
