from fastapi import APIRouter

# это описанеи маршрута и tags для свагера
router = APIRouter(
    prefix="/product",
    tags=["product"],
)

# сам эндпоинт
@router.get("/{product_id}")
def get_product(product_id: int):
    return {"item": product_id}