import json

class Cache:

    def __init__(self, group_id="Group3"):
        self.group_id = group_id
        self.categories = []
        self.areas = []
        self.ingredients = []
        self.loaded = False

    def store_categories(self, data):
        if data and "meals" in data:
            self.categories = [item["strCategory"] for item in data["meals"]]

    def store_areas(self, data):
        if data and "meals" in data:
            self.areas = [item["strArea"] for item in data["meals"]]

    def store_ingredients(self, data):
        if data and "meals" in data:
            self.ingredients = [item["strIngredient"] for item in data["meals"]]

    def get_categories(self):
        return self.categories

    def get_areas(self):
        return self.areas

    def get_ingredients(self, limit=None):
        if limit:
            return self.ingredients[:limit]
        return self.ingredients

    def save_to_file(self):
        filename = f"reference_{self.group_id}.json"
        data = {
            "categories": self.categories,
            "areas": self.areas,
            "ingredients": self.ingredients[:50]
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[Cache] Reference data saved to {filename}")
            return True
        except Exception as e:
            print(f"[Cache Error] Failed to save file: {e}")
            return False

    def is_loaded(self):
        return self.loaded

    def set_loaded(self, status=True):
        self.loaded = status


if __name__ == "__main__":
    cache = Cache("Group3")
    print("cache.py - Module Test")
    print(f"Group ID: {cache.group_id}")
    print(f"Categories loaded: {len(cache.get_categories())}")
    print(f"Areas loaded: {len(cache.get_areas())}")
    print(f"Ingredients loaded: {len(cache.get_ingredients())}")
    print(f"Cache loaded status: {cache.is_loaded()}")