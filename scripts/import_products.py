import csv
import random

from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models import Product

CSV_FILE = "data/styles.csv"
SKIP_CATEGORIES = {"Free Items", "Home", "Sporting Goods"}
GENDER_WORDS = {"men", "women", "boys", "girls", "unisex", "men's", "women's"}
PRICE_RANGES = {
  "Apparel": (590, 4990),
  "Footwear": (990, 8990),
  "Accessories": (290, 4990),
  "Personal Care": (190, 2990),
}
DEFAULT_PRICE_RANGE = (290, 4990)

def read_rows() -> list[dict[str, str]]:
  rows = []
  skipped = 0

  with open(CSV_FILE, encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    header = next(reader)

    for row in reader: 
      if len(row) != len(header):
        skipped += 1
        continue

      product = dict(zip(header, row))

      if product["masterCategory"] in SKIP_CATEGORIES:
        skipped += 1 
        continue
      rows.append(product)

  print("Заголовок", header)
  print("Строк пропущено", skipped)
  print("Строк прочитано", len(rows))
  return rows

def clean(value: str) -> str | None:
  val = value.strip()
  if val == '' or val == 'NA':
    return None
  return val

# так как поля бренд нету, его надо собрать
def extract_brand(name: str) -> str | None:
  words = name.split()
  for i, word in enumerate(words): 
    if word.lower() in GENDER_WORDS:
      return " ".join(words[:i])
  return words[0]
 
# так как цены нету она будет генериться по определенному алгоритму
def generate_price(product_id: int, master_category: str) -> int:
  low, high = PRICE_RANGES.get(master_category, DEFAULT_PRICE_RANGE)
  price = random.Random(product_id).randint(low, high)
  return price // 100 * 100 + 90

def row_to_product(row: dict[str, str]) -> Product:
  product_id = int(row['id'])
  name = row["productDisplayName"].strip()
  year = clean(row["year"])

  return Product(
    id=product_id,
    name=name,
    brand=extract_brand(name),
    gender=row["gender"],
    master_category=row["masterCategory"],
    sub_category=row["subCategory"],
    article_type=row["articleType"],
    colour=clean(row["baseColour"]),
    season=clean(row["season"]),
    year=int(year) if year else None,
    usage=clean(row["usage"]),
    price=generate_price(product_id, row["masterCategory"]),
  )

def main() -> None:
  rows = read_rows()
  products = [row_to_product(row) for row in rows]

  with SessionLocal() as session:
    session.execute(delete(Product))
    session.add_all(products)
    session.commit()

    total = session.scalar(select(func.count()).select_from(Product))
  print("В базе товаров", total)


if __name__ == "__main__":
  main()