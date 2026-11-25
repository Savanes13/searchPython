Ниже — законченный пример аккуратной архитектуры именно для твоего проекта. Важно: «идеальная» не означает максимальное количество слоёв. Для получения товара по
   ID достаточно разделить HTTP-маршруты, схемы ответов, модели и подключение к БД.

   ```text
     Postman
        ↓
     Router FastAPI
        ↓
     Сессия SQLAlchemy
        ↓
     ORM-модель Product
        ↓
     PostgreSQL
        ↓
     Pydantic ProductResponse
        ↓
     JSON
   ```

   Структура получится такой:

   ```text
     app/
     ├── main.py
     ├── database.py
     ├── models.py
     ├── schemas.py
     └── routers/
         ├── __init__.py
         └── products.py
   ```

   1. Модель Product

   Твой app/models.py уже описывает таблицу правильно, менять его не нужно:

   ```python
     from sqlalchemy import String
     from sqlalchemy.orm import Mapped, mapped_column

     from app.database import Base


     class Product(Base):
         __tablename__ = "products"

         id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
         name: Mapped[str] = mapped_column(String(300))
         brand: Mapped[str | None] = mapped_column(String(100), index=True)
         gender: Mapped[str] = mapped_column(String(20), index=True)
         master_category: Mapped[str] = mapped_column(String(50), index=True)
         sub_category: Mapped[str] = mapped_column(String(50), index=True)
         article_type: Mapped[str] = mapped_column(String(50), index=True)
         colour: Mapped[str | None] = mapped_column(String(50))
         season: Mapped[str | None] = mapped_column(String(20))
         year: Mapped[int | None]
         usage: Mapped[str | None] = mapped_column(String(30))
         price: Mapped[int]
   ```

   Это ORM-модель: она описывает данные в базе, а не формат HTTP-ответа.

   2. Управление сессией БД

   В app/database.py оставь существующие engine, SessionLocal и Base. Добавь зависимость:

   ```python
     from collections.abc import Generator

     from sqlalchemy.orm import Session


     def get_db() -> Generator[Session, None, None]:
         db = SessionLocal()

         try:
             yield db
         finally:
             db.close()
   ```

   Если Session уже импортирован в файле, повторный импорт не нужен.

   Что здесь происходит:

   • перед обработкой запроса создаётся сессия;
   • yield db передаёт её эндпоинту;
   • после запроса finally гарантированно закрывает сессию, даже если произошла ошибка.

   3. Схема ответа

   Создай app/schemas.py:

   ```python
     from pydantic import BaseModel, ConfigDict


     class ProductResponse(BaseModel):
         model_config = ConfigDict(from_attributes=True)

         id: int
         name: str
         brand: str | None
         gender: str
         master_category: str
         sub_category: str
         article_type: str
         colour: str | None
         season: str | None
         year: int | None
         usage: str | None
         price: int
   ```

   ProductResponse определяет, какие данные получит клиент.

   ConfigDict(from_attributes=True) позволяет Pydantic читать поля не только из словаря, но и из ORM-объекта:

   ```python
     product.name
     product.price
   ```

   Благодаря response_model=ProductResponse FastAPI сам преобразует объект Product в JSON.

   4. Эндпоинт в отдельном роутере

   Создай пустой файл app/routers/__init__.py, а в app/routers/products.py добавь:

   ```python
     from fastapi import APIRouter, Depends, HTTPException, status
     from sqlalchemy.orm import Session

     from app.database import get_db
     from app.models import Product
     from app.schemas import ProductResponse


     router = APIRouter(
         prefix="/product",
         tags=["products"],
     )


     @router.get("/{product_id}", response_model=ProductResponse)
     def get_product(
         product_id: int,
         db: Session = Depends(get_db),
     ):
         product = db.get(Product, product_id)

         if product is None:
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail=f"Product with id {product_id} not found",
             )

         return product
   ```

   Итоговый адрес остаётся прежним:

   ```text
     GET /product/{product_id}
   ```

   Разбор обработчика:

   ```python
     product_id: int
   ```

   FastAPI получает ID из URL и преобразует его в int. При /product/abc вернёт 422.

   ```python
     db: Session = Depends(get_db)
   ```

   FastAPI создаёт сессию через get_db() и передаёт её в функцию.

   ```python
     product = db.get(Product, product_id)
   ```

   SQLAlchemy ищет запись по первичному ключу Product.id. Вручную писать SQL не требуется.

   ```python
     if product is None:
   ```

   Если запрос выполнен успешно, но запись отсутствует, API возвращает 404.

   ```python
     return product
   ```

   FastAPI проверяет объект через ProductResponse и возвращает клиенту JSON со всеми указанными полями.

   Здесь используется обычный def, потому что текущая сессия SQLAlchemy синхронная.

   5. Подключение роутера к приложению

   Итоговый app/main.py:

   ```python
     from fastapi import FastAPI

     from app.routers import products


     app = FastAPI()

     app.include_router(products.router)


     @app.get("/")
     def root():
         return {"message": "Hello World"}
   ```

   Старый обработчик из main.py нужно убрать:

   ```python
     @app.get("/product/{product_id}")
     async def getProduct(product_id):
         return {"item": product_id}
   ```

   Иначе один и тот же маршрут будет объявлен дважды.

   6. Проверка через Postman

   Перезапусти сервер:

   ```powershell
     fastapi dev app/main.py
   ```

   Запрос существующего товара:

   ```text
     GET http://127.0.0.1:8000/product/123
   ```

   Ответ при успехе — 200 OK:

   ```json
     {
       "id": 123,
       "name": "Название товара",
       "brand": "Бренд",
       "gender": "Men",
       "master_category": "Apparel",
       "sub_category": "Topwear",
       "article_type": "T-shirts",
       "colour": "Black",
       "season": "Summer",
       "year": 2024,
       "usage": "Casual",
       "price": 1999
     }
   ```

   Если товара нет — 404 Not Found:

   ```json
     {
       "detail": "Product with id 123 not found"
     }
   ```

   Если передан нечисловой ID — 422 Unprocessable Entity.

   Когда добавлять service и repository

   Для одного db.get() дополнительные слои пока будут лишними. Когда появятся фильтрация, сложные проверки, изменение нескольких сущностей и другие сценарии,
   структуру можно развить так:

   ```text
     Router → Service → Repository → SQLAlchemy → PostgreSQL
   ```

   • Router — HTTP, статусы и схемы;
   • Service — бизнес-правила;
   • Repository — запросы к данным;
   • Model — структура таблицы.

   Но для текущей задачи показанный вариант является полноценной и чистой архитектурой, а не упрощённым или неправильным решением.