"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""


class Controller:

    def __init__(self, view, restaurant):
        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number):
        self.view.set_controller(TableController(self.view, self.restaurant,
                                                 self.restaurant.tables[table_number]))
        self.view.update()


class TableController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self, printer):
        # TODO: switch to appropriate controller & UI so server can create and print bills
        # for this table. The following line illustrates how bill printing works, but the
        # actual printing should happen in the (new) controller, not here.
        self.view.set_controller(ReceiptController(self.view, self.restaurant, self.table))
        self.view.controller.make_bills()

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()


class ReceiptController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table
        self.receipt = []
        self.total = 0

    def create_ui(self):
        self.view.create_receipt_ui(self.table)

    def make_bills(self):
        self.view.create_receipt_ui(self.table)
        self.restaurant.notify_views()

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()

    def print_bills(self, printer, billing):
        printer.print(f'Bills for Table {self.restaurant.tables.index(self.table)}:')
        total = 0
        for seat, orders in billing.items():
            subtotal = 0
            new = [key for key, value in billing.items() if value == seat]#list of orders for the seat
            if new: #if the seat is paying for an order
                printer.print(" Seat " + str(orders)+":")
            for order in new:
                for item in self.table.orders[order].items:
                    subtotal = subtotal + item.details.price
                    total = total + item.details.price
                    printer.print(f'      {item.details.name:20} $ {item.details.price:.2f}')

            if subtotal != 0:
                printer.print(f' Seat Total{" ":15} $ {subtotal:.2f}')
                printer.print(f' ')  # blank line
        printer.print(f' ')#blank line
        printer.print(f'Table Total:{" ":14} $ {total:.2f}')








