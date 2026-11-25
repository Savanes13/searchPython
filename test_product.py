from app.database import SessionLocal
from app.models import Product

with SessionLocal() as session: 
  product = Product(
    id=1,
    name="Test Men Grey T-shirt",
    brand="Test",
    gender="Men",
    master_category="Apparel",
    sub_category="Topwear",
    article_type="Tshirts",
    price=1990,
  )