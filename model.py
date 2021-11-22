"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from constants import TABLES, MENU_ITEMS


class Restaurant:

    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:

    def __init__(self, seats, location):
        self.n_seats = seats
        self.location = location
        self.orders = [Order() for _ in range(seats)]
        self.receipt = Receipt()

    def has_any_active_orders(self):
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def order_for(self, seat):
        return self.orders[seat]


class Order:

    def __init__(self):
        self.items = []

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item):
        self.items.remove(order_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))


class OrderItem:

    # TODO: need to represent item state, not just 'ordered', all methods will need modifying
    def __init__(self, menu_item):
        self.details = menu_item
        self.ordered = False

    def mark_as_ordered(self):
        self.ordered = True

    def has_been_ordered(self):
        return self.ordered

    def has_been_served(self):
        # TODO: correct implementation based on item state
        return False

    def can_be_cancelled(self):
        # TODO: correct implementation based on item state
        return True


class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price


class Receipt:

    def __init__(self):
        self.seats = []
        self.billing = []

    def update_receipt(self, new_seats, new_billing):
        self.seats = new_seats.copy()
        self.billing = new_billing.copy()

    def print_receipt(self, printer, tablenum, table):
        printer.print(f'Bills for Table {tablenum}:')
        total = 0

        zipped = dict(zip(self.seats, self.billing))

        for seat, orders in zipped.items():
            subtotal = 0
            orders_for_seat = [key for key, value in zipped.items() if value == seat]  # list of orders for the seat
            if orders_for_seat:  # if the seat is paying for an order (not null)
                printer.print(" Seat " + str(orders) + ":")
            for order in orders_for_seat:
                for item in table.orders[order].items:
                    subtotal = subtotal + item.details.price
                    total = total + item.details.price
                    printer.print(f'      {item.details.name:20} $ {item.details.price:.2f}')
            if subtotal != 0:
                printer.print(f' Seat Total{" ":15} $ {subtotal:.2f}')
                printer.print(f' ')  # blank line
        printer.print(f' ')  # blank line
        printer.print(f'Table Total:{" ":14} $ {total:.2f}')


