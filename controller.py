"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""
import os.path
from datetime import datetime

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


class Ledger(Controller):
    def __init__(self, view, restaurant):
        super().__init__(view, restaurant)
        self.receipts=[]


    def copy_bills(self, billing, table):
        date = datetime.now().strftime("%Y_%m_%d-%I-%M-%S_%p")#This has a limitation that only one recipt can be printed
                                                            #per minute. In the real world, this seems reasonable.
                                                            #Otherwise, the record will be overwritten.
        if not os.path.isdir("receipts"): #Checks if the receipt folder exists
            os.makedirs("receipts")         #creates the folder if needed
        filepath=os.path.join('receipts',f'Table_{self.restaurant.tables.index(table)}_on_{date}.txt')
        f = open(filepath,"w")
        total = 0
        for seat, orders in billing.items():
            subtotal = 0
            new = [key for key, value in billing.items() if value == seat]#list of orders for the seat
            if new: #if the seat is paying for an order
                f.write(" Seat " + str(orders)+":\n")
            for order in new:
                for item in table.orders[order].items:
                    subtotal = subtotal + item.details.price
                    total = total + item.details.price
                    f.write(f'      {item.details.name:20} $ {item.details.price:.2f}\n')

            if subtotal != 0:
                f.write(f' Seat Total{" ":15} $ {subtotal:.2f}\n')
                f.write(f'\n')  # blank line
        f.write(f'\n')#blank line
        f.write(f'Table Total:{" ":14} $ {total:.2f}\n')
        self.receipts.append(filepath)


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
            orders_for_seat= [key for key, value in billing.items() if value == seat]#list of orders for the seat
            if orders_for_seat: #if the seat is paying for an order (not null)
                printer.print(" Seat " + str(orders)+":")
            for order in orders_for_seat:
                for item in self.table.orders[order].items:
                    subtotal = subtotal + item.details.price
                    total = total + item.details.price
                    printer.print(f'      {item.details.name:20} $ {item.details.price:.2f}')
            if subtotal != 0:
                printer.print(f' Seat Total{" ":15} $ {subtotal:.2f}')
                printer.print(f' ')  # blank line
        printer.print(f' ')#blank line
        printer.print(f'Table Total:{" ":14} $ {total:.2f}')
        self.total = total
        self.create_ui()

    def checktotal(self):
        i = 12
        return self.total

    def cleanup(self, billing):
        self.view.ledger.copy_bills(billing,self.table)

        for order in self.table.orders:
            order.items.clear()
        self.view.set_controller(RestaurantController(self.view,self.restaurant))
        self.restaurant.notify_views()










