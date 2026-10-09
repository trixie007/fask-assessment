from flask import Flask, jsonify, request
from external_api import fetch_product

app = Flask(__name__)

# Temporary storage for inventory items
inventory = []

# Keeps IDs unique
next_id = 1


# GET /inventory
# Fetch all inventory items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


# GET /inventory/<id>
# Fetch a single inventory item
@app.route("/inventory/<int:id>", methods=["GET"])
def get_item(id):
    for item in inventory:
        if item["id"] == id:
            return jsonify(item), 200

    return jsonify({"error": "Item not found"}), 404


# POST /inventory
# Add a new inventory item
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    required_fields = ["name", "quantity", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    if not isinstance(data["quantity"], int) or data["quantity"] < 0:
        return jsonify({
            "error": "Quantity must be a non-negative integer"
        }), 400

    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({
            "error": "Price must be a non-negative number"
        }), 400

    # Create inventory item
    item = {
        "id": next_id,
        "name": data["name"],
        "quantity": data["quantity"],
        "price": data["price"]
    }

    # Look up additional product information
    product = None

    if data.get("barcode"):
        product = fetch_product(
            barcode=data["barcode"]
        )

    elif data.get("name"):
        product = fetch_product(
            name=data["name"]
        )

    # Add OpenFoodFacts information
    if product:
        item["barcode"] = product.get("barcode")
        item["brand"] = product.get("brand")
        item["category"] = product.get("category")
        item["ingredients"] = product.get("ingredients")
        item["image"] = product.get("image")

    inventory.append(item)
    next_id += 1

    return jsonify(item), 201


# PATCH /inventory/<id>
# Update an inventory item
@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_item(id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    for item in inventory:
        if item["id"] == id:

            if "name" in data:
                item["name"] = data["name"]

            if "quantity" in data:
                if (
                    not isinstance(data["quantity"], int)
                    or data["quantity"] < 0
                ):
                    return jsonify({
                        "error": "Quantity must be a non-negative integer"
                    }), 400

                item["quantity"] = data["quantity"]

            if "price" in data:
                if (
                    not isinstance(data["price"], (int, float))
                    or data["price"] < 0
                ):
                    return jsonify({
                        "error": "Price must be a non-negative number"
                    }), 400

                item["price"] = data["price"]

            return jsonify(item), 200

    return jsonify({
        "error": "Item not found"
    }), 404


# DELETE /inventory/<id>
# Delete an inventory item
@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_item(id):
    for item in inventory:
        if item["id"] == id:
            inventory.remove(item)

            return jsonify({
                "message": "Item deleted"
            }), 200

    return jsonify({
        "error": "Item not found"
    }), 404


# GET /looku
# Search OpenFoodFacts by barcode or product name
@app.route("/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({
            "error": "Provide a barcode or product name"
        }), 400

    product = fetch_product(
        barcode=barcode,
        name=name
    )

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(product), 200


if __name__ == "__main__":
    app.run(debug=True)