import json

class ProductItem:
    def __init__(self, url, category, main_type, sub_type, brand, name, price, currency, image_urls, composition, highlights):
        self.url = url
        self.category = category
        self.main_type = main_type
        self.sub_type = sub_type
        self.brand = brand
        self.name = name
        self.price = price
        self.currency = currency
        self.image_urls = image_urls
        self.composition = composition
        self.highlights = highlights

    def to_dict(self):
        """Chuyển object thành dictionary"""
        return {
            "url": self.url,
            "category": self.category,
            "main_type": self.main_type,
            "sub_type": self.sub_type,
            "brand": self.brand,
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "image_urls": self.image_urls,
            "composition": self.composition,
            "highlights": self.highlights,
        }

    def save_to_jsonl(self, filename):
        """Ghi đối tượng ra file JSONL"""
        with open(filename, "a", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False)
            file.write("\n")  # Xuống dòng để lưu dạng JSONL