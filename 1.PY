import sys
import json
import time
import datetime
import random

class MenuItem:
    def __init__(self, id, name, price, category, veg=True):
        self.id = id
        self.name = name
        self.price = float(price)
        self.category = category
        self.veg = veg

class Menu:
    def __init__(self):
        self.items = {}
        self.load_default_menu()

    def load_default_menu(self):
        preset = [
            (1, "Veg Spring Roll (2 pcs)", 80, "Starters", True),
            (2, "Paneer Tikka", 160, "Starters", True),
            (3, "Chicken 65", 180, "Starters", False),
            (4, "Veg Supreme Pizza (8\")", 420, "Mains", True),
            (5, "Margherita Pizza (8\")", 380, "Mains", True),
            (6, "Butter Chicken", 260, "Mains", False),
            (7, "Paneer Butter Masala", 240, "Mains", True),
            (8, "Grilled Fish", 300, "Mains", False),
            (9, "Veg Fried Rice", 140, "Rice/Noodles", True),
            (10, "Egg Fried Rice", 150, "Rice/Noodles", False),
            (11, "Chicken Biryani (Single)", 220, "Rice/Noodles", False),
            (12, "Gulab Jamun (2 pcs)", 60, "Desserts", True),
            (13, "Chocolate Brownie", 90, "Desserts", True),
            (14, "Cold Coffee", 90, "Beverages", True),
            (15, "Fresh Lime Soda", 50, "Beverages", True),
            (16, "Masala Soda", 60, "Beverages", True)
        ]
        for id, name, price, cat, veg in preset:
            self.items[id] = MenuItem(id, name, price, cat, veg)

    def display(self, veg_filter=None):
        grouped = {}
        for item in self.items.values():
            if veg_filter is None or (veg_filter and item.veg) or (not veg_filter and not item.veg):
                grouped.setdefault(item.category, []).append(item)
        for cat in sorted(grouped.keys()):
            print(f"\n--- {cat} ---")
            for it in grouped[cat]:
                v = "Veg" if it.veg else "Non-Veg"
                print(f"{it.id}. {it.name} — ₹{format(it.price, '.2f')} [{v}]")

    def get_item(self, id):
        return self.items.get(id)

    def suggest_daily_special(self):
        candidates = list(self.items.values())
        choice = random.choice(candidates)
        return choice

class Order:
    def _init_(self):
        self.lines = {}
        self.created_at = datetime.datetime.now()

    def add(self, item: MenuItem, qty):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        prev = self.lines.get(item.id, {"item": item, "qty": 0})
        prev["qty"] += qty
        self.lines[item.id] = prev

    def remove(self, item_id):
        if item_id in self.lines:
            del self.lines[item_id]
        else:
            raise KeyError("Item not in order")

    def is_empty(self):
        return len(self.lines) == 0

    def subtotal(self):
        total = 0.0
        for entry in self.lines.values():
            total += entry["item"].price * entry["qty"]
        return total

    def breakdown(self):
        lines = []
        for e in self.lines.values():
            name = e["item"].name
            qty = e["qty"]
            rate = e["item"].price
            amt = rate * qty
            lines.append((name, qty, rate, amt))
        return lines

class RestaurantChatbot:
    def __init__(self):
        self.menu = Menu()
        self.order = None
        self.tax_percent = 5.0
        self.service_percent = 2.0
        self.orders_file = "orders.txt"
        self.reviews_file = "reviews.txt"

    def greet(self):
        print("Welcome to Foodie Indian Chatbot!")
        print("I'm your virtual assistant. I can show the menu, take orders, calculate bills and collect reviews.")
        print("Type 'help' to see available commands.\n")

    def help(self):
        cmds = [
            ("menu", "Show full menu"),
            ("menu veg", "Show only veg items"),
            ("menu nonveg", "Show only non-veg items"),
            ("special", "Show today's special suggestion"),
            ("start", "Start a new order"),
            ("add", "Add item to current order"),
            ("remove", "Remove item from current order"),
            ("show", "Show current order summary"),
            ("checkout", "Checkout and calculate bill"),
            ("review", "Leave a review"),
            ("exit", "Exit chatbot")
        ]
        print("\nCommands:")
        for c, d in cmds:
            print(f"{c:12} - {d}")
        print()

    def run(self):
        self.greet()
        while True:
            try:
                cmd = input(">>> ").strip().lower()
                if not cmd:
                    continue
                if cmd == "help":
                    self.help()
                elif cmd == "menu":
                    self.menu.display()
                elif cmd == "menu veg":
                    self.menu.display(veg_filter=True)
                elif cmd == "menu nonveg":
                    self.menu.display(veg_filter=False)
                elif cmd == "special":
                    s = self.menu.suggest_daily_special()
                    tag = "Veg" if s.veg else "Non-Veg"
                    print(f"Today's special: {s.name} — ₹{format(s.price, '.2f')} [{tag}]")
                elif cmd == "start":
                    if self.order and not self.order.is_empty():
                        print("You have an active order. Use 'show' or 'checkout' or start a new one by typing 'start new'.")
                        continue
                    self.order = Order()
                    print("New order started. Use 'add' to add items.")
                elif cmd.startswith("start "):
                    if cmd.split()[1] == "new":
                        self.order = Order()
                        print("New order started.")
                    else:
                        print("Unknown start option.")
                elif cmd == "add":
                    if self.order is None:
                        print("No active order. Type 'start' to begin.")
                        continue
                    try:
                        id_str = input("Item ID: ").strip()
                        qty_str = input("Quantity: ").strip()
                        if not id_str.isdigit() or not qty_str.isdigit():
                            raise ValueError("ID and Quantity must be numbers")
                        item_id = int(id_str)
                        qty = int(qty_str)
                        item = self.menu.get_item(item_id)
                        if item is None:
                            print("Item ID not found.")
                            continue
                        self.order.add(item, qty)
                        print(f"Added {qty} x {item.name}")
                    except Exception as e:
                        print("Error adding item:", e)
                elif cmd == "remove":
                    if self.order is None or self.order.is_empty():
                        print("No items to remove.")
                        continue
                    try:
                        id_str = input("Item ID to remove: ").strip()
                        if not id_str.isdigit():
                            raise ValueError("ID must be a number")
                        item_id = int(id_str)
                        self.order.remove(item_id)
                        print("Item removed.")
                    except Exception as e:
                        print("Error:", e)
                elif cmd == "show":
                    if self.order is None or self.order.is_empty():
                        print("No active order or order is empty.")
                        continue
                    self.print_order_summary(self.order)
                elif cmd == "checkout":
                    if self.order is None or self.order.is_empty():
                        print("No active order to checkout.")
                        continue
                    self.checkout()
                elif cmd == "review":
                    self.collect_review()
                elif cmd == "exit":
                    print("Thank you for using Foodie Indian Chatbot. Goodbye!")
                    break
                else:
                    print("Unknown command. Type 'help' to see commands.")
            except KeyboardInterrupt:
                print("\nSession ended by user.")
                break
            except Exception as e:
                print("Unexpected error:", e)

    def print_order_summary(self, order: Order):
        print("\nOrder Summary:")
        lines = order.breakdown()
        for name, qty, rate, amt in lines:
            print(f"{name} x{qty} @ ₹{format(rate, '.2f')} = ₹{format(amt, '.2f')}")
        subtotal = order.subtotal()
        tax = (subtotal * self.tax_percent) / 100.0
        service = (subtotal * self.service_percent) / 100.0
        total = subtotal + tax + service
        print(f"\nSubtotal: ₹{format(subtotal, '.2f')}")
        print(f"Tax ({format(self.tax_percent, '.1f')}%): ₹{format(tax, '.2f')}")
        print(f"Service ({format(self.service_percent, '.1f')}%): ₹{format(service, '.2f')}")
        print(f"Total: ₹{format(total, '.2f')}\n")

    def checkout(self):
        self.print_order_summary(self.order)
        while True:
            conf = input("Confirm order? (y/n): ").strip().lower()
            if conf == "y":
                self.save_order(self.order)
                print("Order confirmed and saved. Thank you!")
                self.order = None
                break
            elif conf == "n":
                print("Order cancelled.")
                self.order = None
                break
            else:
                print("Please enter 'y' or 'n'.")

    def save_order(self, order: Order):
        data = {
            "timestamp": order.created_at.isoformat(),
            "items": [],
            "subtotal": float(format(order.subtotal(), ".2f")),
            "tax_percent": self.tax_percent,
            "service_percent": self.service_percent
        }
        tax = (data["subtotal"] * self.tax_percent) / 100.0
        service = (data["subtotal"] * self.service_percent) / 100.0
        total = data["subtotal"] + tax + service
        data["tax_amount"] = float(format(tax, ".2f"))
        data["service_amount"] = float(format(service, ".2f"))
        data["total"] = float(format(total, ".2f"))
        for e in order.breakdown():
            name, qty, rate, amt = e
            data["items"].append({
                "name": name,
                "qty": int(qty),
                "rate": float(format(rate, ".2f")),
                "amount": float(format(amt, ".2f"))
            })
        try:
            with open(self.orders_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print("Failed to save order:", e)

    def collect_review(self):
        try:
            name = input("Your name (optional): ").strip()
            rating_str = input("Rating 1-5: ").strip()
            if not rating_str.isdigit():
                print("Invalid rating. Must be 1-5 numeric.")
                return
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                print("Rating must be between 1 and 5.")
                return
            comment = input("Comments (optional): ").strip()
            entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "name": name if name else "Anonymous",
                "rating": rating,
                "comment": comment
            }
            with open(self.reviews_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            print("Thanks for your feedback!")
        except Exception as e:
            print("Failed to record review:", e)

if __name__ == "__main__":
    random.seed(int(time.time()))
    bot = RestaurantChatbot()
    bot.run()