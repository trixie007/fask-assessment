
import requests

API_URL = "http://127.0.0.1:5000"


def handle_response(response):
    """Handle API responses and display errors."""
    try:
        data = response.json()
    except ValueError:
        print("Error: Server returned an invalid response.")
        return None

    if response.status_code >= 400:
        print(f"Error: {data.get('error', 'API request failed')}")
        return None

    return data


def add_item():
    """Add a new inventory item."""
    print("\n--- Add New Inventory Item ---")

    name = input("Enter product name: ").strip()

    if not name:
        print("Error: Product name cannot be empty.")
        return

    try:
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price: "))

        if quantity < 0 or price < 0:
            print("Error: Quantity and price cannot be negative.")
            return

    except ValueError:
        print("Error: Enter valid numbers for quantity and price.")
        return

    barcode = input("Enter barcode (optional): ").strip()

    data = {
        "name": name,
        "quantity": quantity,
        "price": price
    }

    if barcode:
        data["barcode"] = barcode

    try:
        response = requests.post(
            f"{API_URL}/inventory",
            json=data,
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            print("\nItem added successfully!")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def list_items():
    """Display all inventory items."""
    print("\n--- Inventory Items ---")

    try:
        response = requests.get(
            f"{API_URL}/inventory",
            timeout=10
        )

        result = handle_response(response)

        if result is None:
            return

        if not result:
            print("Inventory is empty.")
            return

        for item in result:
            print(f"\nID: {item['id']}")
            print(f"Name: {item['name']}")
            print(f"Quantity: {item['quantity']}")
            print(f"Price: {item['price']}")
            print("-" * 25)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def get_item():
    """Display one inventory item."""
    try:
        item_id = int(input("Enter the product ID: "))
    except ValueError:
        print("Error: ID must be a number.")
        return

    try:
        response = requests.get(
            f"{API_URL}/inventory/{item_id}",
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            print("\nProduct details:")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def update_item():
    """Update the price or quantity of an item."""
    try:
        item_id = int(input("Enter the product ID to update: "))
    except ValueError:
        print("Error: ID must be a number.")
        return

    print("\nWhat would you like to update?")
    print("1. Price")
    print("2. Quantity")
    print("3. Both")

    choice = input("Choose an option: ").strip()
    data = {}

    if choice in ("1", "3"):
        try:
            price = float(input("Enter the new price: "))
            if price < 0:
                print("Error: Price cannot be negative.")
                return
            data["price"] = price
        except ValueError:
            print("Error: Enter a valid price.")
            return

    if choice in ("2", "3"):
        try:
            quantity = int(input("Enter the new quantity: "))
            if quantity < 0:
                print("Error: Quantity cannot be negative.")
                return
            data["quantity"] = quantity
        except ValueError:
            print("Error: Enter a valid quantity.")
            return

    if not data:
        print("Invalid choice. Please choose 1, 2, or 3.")
        return

    try:
        response = requests.patch(
            f"{API_URL}/inventory/{item_id}",
            json=data,
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            print("\nItem updated successfully!")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def delete_item():
    """Delete an inventory item."""
    try:
        item_id = int(input("Enter the product ID to delete: "))
    except ValueError:
        print("Error: ID must be a number.")
        return

    confirm = input(
        f"Are you sure you want to delete item {item_id}? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Deletion cancelled.")
        return

    try:
        response = requests.delete(
            f"{API_URL}/inventory/{item_id}",
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            print("Delete request completed.")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def find_product():
    """Find a product using OpenFoodFacts."""
    print("\n--- Find a Product ---")
    print("1. Search by barcode")
    print("2. Search by product name")

    choice = input("Choose a search method: ").strip()

    if choice == "1":
        value = input("Enter the product barcode: ").strip()
        params = {"barcode": value}
    elif choice == "2":
        value = input("Enter the product name: ").strip()
        params = {"name": value}
    else:
        print("Invalid choice.")
        return

    if not value:
        print("Error: Search value cannot be empty.")
        return

    try:
        response = requests.get(
            f"{API_URL}/lookup",
            params=params,
            timeout=10
        )

        result = handle_response(response)

        if result is not None:
            print("\nProduct found:")
            print(result)

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")


def main():
    """Display the interactive inventory menu."""
    while True:
        print("\n================================")
        print(" RETAIL INVENTORY MANAGEMENT")
        print("================================")
        print("1. Add an inventory item")
        print("2. View all inventory items")
        print("3. View one inventory item")
        print("4. Update an inventory item")
        print("5. Delete an inventory item")
        print("6. Find a product using OpenFoodFacts")
        print("7. Exit")
        print("================================")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_item()
        elif choice == "2":
            list_items()
        elif choice == "3":
            get_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            find_product()
        elif choice == "7":
            print("Thank you for using the inventory system!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()

