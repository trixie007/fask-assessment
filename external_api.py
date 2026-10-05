import requests


OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v2"

HEADERS = {
    "User-Agent": "RetailInventoryApp/1.0"
}


def format_product(product):
    return {
        "name": product.get("product_name"),
        "barcode": product.get("code"),
        "brand": product.get("brands"),
        "category": product.get("categories"),
        "ingredients": product.get("ingredients_text"),
        "image": product.get("image_url")
    }


def fetch_product(barcode=None, name=None):
    """
    Fetch product details from OpenFoodFacts
    using either a barcode or product name.
    """

    # Search by barcode
    if barcode:
        url = f"{OPENFOODFACTS_URL}/product/{barcode}"

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("status") != 1:
            return None

        product = data.get("product", {})

        return format_product(product)

    # Search by product name
    if name:
        url = f"{OPENFOODFACTS_URL}/search"

        params = {
            "categories_tags_en": name,
            "page_size": 1,
            "fields": (
                "product_name,"
                "code,"
                "brands,"
                "categories,"
                "ingredients_text,"
                "image_url"
            )
        }

        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        products = data.get("products", [])

        if not products:
            return None

        return format_product(products[0])

    return None