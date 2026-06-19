# Исправление US-B2B-11: дополнение SKUResponse

## Описание
Дополнена схема `SKUResponse` обязательными полями из спецификации `b2b/openapi.yaml`. Теперь `PATCH /api/v1/skus/{sku_id}` возвращает полный контракт ответа.

## Изменения

### 1. Схема `SKUResponse` (`src/schemas/product.py`)
Добавлены обязательные поля согласно `b2b/openapi.yaml`:
- `name` — название SKU
- `discount` — скидка в копейках
- `cost_price` — себестоимость (nullable)
- `active_quantity` — `stock_quantity - reserved_quantity`
- `article` — артикул (nullable)
- `images` — массив изображений с полями `id`, `url`, `ordering`
- `characteristics` — массив характеристик с полями `id`, `name`, `value`

### 2. Сервисный слой (`src/services/product_service.py`)
- Введён метод `_build_full_sku_response()` для централизованного формирования полного SKU-ответа
- Обновлён `create_sku()` — новые SKU создаются с полными полями
- Обновлён `update_sku()` — возвращает полный SKU-ответ
- Обновлён `_enrich_skus_for_seller()` — использует `_build_full_sku_response()`

### 3. Обратная совместимость
Если в SKU есть старое поле `image` (одиночный URL), оно автоматически преобразуется в массив `images` с одним элементом.

## ADR: Централизация формирования SKU-ответа

**Контекст:** SKU-ответ используется в нескольких местах (create_sku, update_sku, _enrich_skus_for_seller). При дублировании логики высок риск расхождения полей.

**Рассмотренные альтернативы:**
1. **Pydantic-сериализатор с `from_attributes=True`** — требует ORM-моделей, но SKU хранится как JSON внутри Product.
2. **Отдельные функции для каждого endpoint** — дублирование кода, риск рассинхронизации.
3. **Единый метод `_build_full_sku_response()`** — одно место правды.

**Выбрано:** Вариант 3.

**Критерии:**
- **N+1 проблема:** Не возникает, т.к. SKU уже загружены как JSON вместе с Product.
- **Сложность поддержки:** Все изменения в контракте SKU делаются в одном месте.

## Лог тестов (DoD)
platform win32 -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\matvey_chertovikov\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\US-B2B\-US-B2B-03
plugins: anyio-4.13.0
collected 6 items                                                                                   

tests/test_seller_products.py::TestSellerProductsList::test_list_returns_only_own_products PASSED [ 16%]
tests/test_seller_products.py::TestSellerProductsList::test_idor_query_param_seller_id_ignored PASSED [ 33%]
tests/test_seller_products.py::TestSellerProductsList::test_deleted_products_visible_with_deleted_flag PASSED [ 50%]
tests/test_seller_products.py::TestSellerProductsList::test_status_filter_works_correctly PASSED [ 66%]
tests/test_seller_products.py::TestSellerProductsList::test_search_by_title_case_insensitive PASSED [ 83%]
tests/test_seller_products.py::TestSellerProductsList::test_response_includes_skus_count_and_total_active_quantity PASSED [100%]
