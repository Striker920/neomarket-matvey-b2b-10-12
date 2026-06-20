# US-B2B-11: Дополнение SellerProductItem обязательными полями

## Описание
Реализованы финальные исправления для полного соответствия спецификации `b2b/openapi.yaml`. Endpoint `GET /api/v1/products` в seller-режиме (Bearer JWT) теперь возвращает товары с полными полями согласно контракту.

**Бизнес-контекст:** Продавец в личном кабинете видит список своих товаров. Клиент (фронтенд кабинета) ожидает обязательные поля `slug`, `category_id`, `deleted` — без них UI не может построить ссылки, фильтры и индикаторы статуса.

## Соответствие канон-флоу

### Happy path
- ✅ **list_returns_only_own_products** — продавец видит только свои товары (seller_id из JWT)
- ✅ **response_includes_skus_count_and_total_active_quantity** — ответ содержит агрегаты по SKU

### Unhappy path
- ✅ **idor_query_param_seller_id_ignored** — попытка подменить seller_id через query-param игнорируется
- ✅ **deleted_products_hidden_by_default** — удалённые товары скрыты по умолчанию
- ✅ **deleted_products_visible_with_include_deleted** — удалённые видны при `include_deleted=true`
- ✅ **status_filter_works_correctly** — фильтр по status работает
- ✅ **search_by_title_case_insensitive** — поиск по title регистронезависимый

## Соответствие OpenAPI (b2b/openapi.yaml:1374-1384)

- ✅ `ProductShortResponse` required: `[id, title, slug, status, category_id, deleted, created_at]`
- ✅ Поле `category` (вложенный dict) **не заменяет** `category_id` (UUID) — это два разных поля
- ✅ Параметр `include_deleted` для управления видимостью удалённых товаров

## Внесённые исправления

### 1. Исправлен импорт UUID (`src/schemas/seller_products.py`)
Добавлен `from uuid import UUID` — ранее использовался без импорта.

### 2. Поля в SellerProductItem
Добавлены обязательные поля согласно `b2b/openapi.yaml:1374-1384`:
- `slug: str`
- `category_id: UUID`
- `deleted: bool`

### 3. Поля в ответе (`src/services/product_service.py`)
Метод `get_seller_products_list` теперь возвращает `slug`, `category_id`, `deleted` в каждом элементе.

### 4. Параметр `include_deleted` (`src/api/products.py`)
Добавлен query-параметр `include_deleted` (по умолчанию `False`):
- `False` — возвращает только неудалённые товары (`Product.deleted == False`)
- `True` — возвращает все, включая удалённые

### 5. Очистка БД между тестами (`tests/conftest.py`)
Добавлена очистка таблицы `Product` перед каждым тестом — это устранило накопление данных и ложные падения.

### 6. Обновлены тесты (`tests/test_seller_products.py`)
- Разделён тест `test_deleted_products_visible_with_deleted_flag` на два:
  - `test_deleted_products_hidden_by_default` — проверка скрытия по умолчанию
  - `test_deleted_products_visible_with_include_deleted` — проверка показа при `include_deleted=true`
- Добавлены проверки наличия новых полей во всех тестах

## ADR: Управление видимостью удалённых товаров

**Контекст:** Продавцу нужно видеть удалённые товары в кабинете (для восстановления или анализа), но по умолчанию они должны быть скрыты, чтобы не засорять основной список.

**Рассмотренные альтернативы:**

1. **Всегда показывать удалённые** — неудобно, засоряет список, путает пользователей
2. **Никогда не показывать** — продавец не может восстановить товар или увидеть историю
3. **Параметр `include_deleted`** — гибко, соответствует REST-практикам

**Выбрано:** Вариант 3 — параметр `include_deleted`.

**Критерии:**
- **UX:** По умолчанию чистый список, но есть доступ к удалённым
- **REST-совместимость:** Стандартный подход для фильтрации в API (аналогично GitHub API, Stripe API)
- **Обратная совместимость:** Значение по умолчанию `False` — старое поведение сохраняется для клиентов, не знающих о параметре

## ADR: Разделение полей `category` и `category_id`

**Контекст:** В схеме `ProductShortResponse` есть поле `category` (вложенный dict с `id` и `name`) и отдельное поле `category_id` (UUID). Это может показаться дублированием.

**Выбрано:** Оставить оба поля.

**Обоснование:**
- `category_id` — для программных клиентов, которым нужен только ID (например, для построения ссылок)
- `category` — для UI, которому нужно сразу отображать название категории без дополнительного запроса
- Это соответствует принципу "flat for machines, nested for humans" в API-дизайне

## Лог тестов (DoD)
platform win32 -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\matvey_chertovikov\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\neomarket-matvey-b2b-10-12-fix-us-b2b-11-sku-response
plugins: anyio-4.13.0
collected 7 items                                                                      

tests/test_seller_products.py::TestSellerProductsList::test_list_returns_only_own_products PASSED [ 14%]
tests/test_seller_products.py::TestSellerProductsList::test_idor_query_param_seller_id_ignored PASSED [ 28%]
tests/test_seller_products.py::TestSellerProductsList::test_deleted_products_hidden_by_default PASSED [ 42%]
tests/test_seller_products.py::TestSellerProductsList::test_deleted_products_visible_with_include_deleted PASSED [ 57%]
tests/test_seller_products.py::TestSellerProductsList::test_status_filter_works_correctly PASSED [ 71%]
tests/test_seller_products.py::TestSellerProductsList::test_search_by_title_case_insensitive PASSED [ 85%]
tests/test_seller_products.py::TestSellerProductsList::test_response_includes_skus_count_and_total_active_quantity PASSED [100%]

================================== warnings summary ===================================
