import argparse
import requests


API_URL = "http://127.0.0.1:5000"


def handle_response(response):
    """Handle API responses and display useful errors."""

    try:
        data = response.json()
    except ValueError:
        print("Error: Server returned an invalid response.")
        return None

    if response.status_code >= 400:
        print(f"Error: {data.get('error', 'API request failed')}")
        return None

    return data


def add_item(args):
    """Add a new inventory item."""

    data = {
        "name": args.name,
        "quantity": args.quantity,
        "price": args.price
    }

    if args.barcode:
        data["barcode"] = args.barcode

    try:
        response = requests.post(
            f"{API_URL}/inventory",
            json=data,
            timeout=10
        )

        result = handle_response(response)

        if result:
            print("Item added successfully.")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def list_items(args):
    """Display all inventory items."""

    try:
        response = requests.get(
            f"{API_URL}/inventory",
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            if not result:
                print("Inventory is empty.")
            else:
                for item in result:
                    print(
                        f"ID: {item['id']} | "
                        f"Name: {item['name']} | "
                        f"Quantity: {item['quantity']} | "
                        f"Price: {item['price']}"
                    )

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def get_item(args):
    """Display one inventory item."""

    try:
        response = requests.get(
            f"{API_URL}/inventory/{args.id}",
            timeout=10
        )

        result = handle_response(response)

        if result:
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def update_item(args):
    """Update an item's price or quantity."""

    data = {}

    if args.price is not None:
        data["price"] = args.price

    if args.quantity is not None:
        data["quantity"] = args.quantity

    if not data:
        print("Error: Provide --price or --quantity.")
        return

    try:
        response = requests.patch(
            f"{API_URL}/inventory/{args.id}",
            json=data,
            timeout=10
        )

        result = handle_response(response)

        if result:
            print("Item updated successfully.")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def delete_item(args):
    """Delete an inventory item."""

    try:
        response = requests.delete(
            f"{API_URL}/inventory/{args.id}",
            timeout=10
        )

        result = handle_response(response)

        if result:
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def find_product(args):
    """Find a product using the OpenFoodFacts API."""

    if not args.barcode and not args.name:
        print("Error: Provide --barcode or --name.")
        return

    params = {}

    if args.barcode:
        params["barcode"] = args.barcode
    else:
        params["name"] = args.name

    try:
        response = requests.get(
            f"{API_URL}/lookup",
            params=params,
            timeout=10
        )

        result = handle_response(response)

        if result:
            print("Product found:")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Retail Inventory Management CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ADD
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new inventory item"
    )

    add_parser.add_argument(
        "--name",
        required=True,
        help="Product name"
    )

    add_parser.add_argument(
        "--quantity",
        required=True,
        type=int,
        help="Stock quantity"
    )

    add_parser.add_argument(
        "--price",
        required=True,
        type=float,
        help="Product price"
    )

    add_parser.add_argument(
        "--barcode",
        help="Product barcode"
    )

    add_parser.set_defaults(func=add_item)

    # LIST
    list_parser = subparsers.add_parser(
        "list",
        help="View all inventory items"
    )

    list_parser.set_defaults(func=list_items)

    # GET
    get_parser = subparsers.add_parser(
        "get",
        help="View one inventory item"
    )

    get_parser.add_argument(
        "id",
        type=int,
        help="Inventory item ID"
    )

    get_parser.set_defaults(func=get_item)

    # UPDATE
    update_parser = subparsers.add_parser(
        "update",
        help="Update price or stock quantity"
    )

    update_parser.add_argument(
        "id",
        type=int,
        help="Inventory item ID"
    )

    update_parser.add_argument(
        "--price",
        type=float,
        help="New product price"
    )

    update_parser.add_argument(
        "--quantity",
        type=int,
        help="New stock quantity"
    )

    update_parser.set_defaults(func=update_item)

    # DELETE
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an inventory item"
    )

    delete_parser.add_argument(
        "id",
        type=int,
        help="Inventory item ID"
    )

    delete_parser.set_defaults(func=delete_item)

    # FIND
    find_parser = subparsers.add_parser(
        "find",
        help="Find a product using OpenFoodFacts"
    )

    find_parser.add_argument(
        "--barcode",
        help="Search using barcode"
    )

    find_parser.add_argument(
        "--name",
        help="Search using product name"
    )

    find_parser.set_defaults(func=find_product)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()