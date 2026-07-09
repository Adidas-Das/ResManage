# frames/dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from db import (
  get_available_table,
  mark_table_unavailable,
  add_customer,
  create_order,
  get_all_orders,
  get_order_items,
  reset_database,
  complete_order,
  release_table,
  hide_order
)


class DashboardFrame(tk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app

    # Header
    header = tk.Frame(self)
    header.pack(fill="x", pady=10)

    title = tk.Label(
      header,
      text="Restaurant Dashboard",
      font=("Arial", 18, "bold")
    )
    title.pack(side="left", padx=20)

    analytics_btn = tk.Button(
      header,
      text="Analytics",
      width=12,
      command=self.open_analytics
    )
    analytics_btn.pack(side="right", padx=10)

    add_customer_btn = tk.Button(
      header,
      text="Add New Customer",
      width=18,
      command=self.add_customer
    )
    add_customer_btn.pack(side="right", padx=10)

    # Orders Table
    columns = (
      "customer_id",
      "table_no",
      "category",
      "status",
      "details",
      "action"
    )

    self.tree = ttk.Treeview(
      self,
      columns=columns,
      show="headings",
      height=18
    )

    self.tree.heading("customer_id", text="Customer ID")
    self.tree.heading("table_no", text="Table No")
    self.tree.heading("category", text="Category")
    self.tree.heading("status", text="Status")
    self.tree.heading("details", text="Order Details")
    self.tree.heading("action", text="Action")

    # Explicit column widths (THIS IS THE KEY FIX)
    self.tree.column("customer_id", width=120, anchor="center", stretch=False)
    self.tree.column("table_no", width=100, anchor="center", stretch=False)
    self.tree.column("category", width=140, anchor="center", stretch=False)
    self.tree.column("status", width=120, anchor="center", stretch=False)
    self.tree.column("details", width=160, anchor="center", stretch=False)
    self.tree.column("action", width=120, anchor="center", stretch=False)

    scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.bind("<Double-1>", self.on_row_action)


    scrollbar.pack(side="right", fill="y")
    self.tree.pack(fill="both", expand=True, padx=20, pady=20)


    for col in columns:
      self.tree.column(col, anchor="center")

    self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    self.load_orders()

  def tkraise(self, aboveThis=None):
    super().tkraise(aboveThis)
    self.load_orders()


  def add_customer(self):
    win = tk.Toplevel(self)
    win.title("Add New Customer")
    win.geometry("350x300")
    win.grab_set()

    tk.Label(win, text="Customer Name").pack(pady=5)
    name_entry = tk.Entry(win)
    name_entry.pack()

    tk.Label(win, text="Phone").pack(pady=5)
    phone_entry = tk.Entry(win)
    phone_entry.pack()

    tk.Label(win, text="Table Category").pack(pady=10)

    category_var = tk.StringVar(value="2-seater")

    categories = ["2-seater", "4-seater", "family"]
    for cat in categories:
      tk.Radiobutton(
        win,
        text=cat,
        variable=category_var,
        value=cat
      ).pack(anchor="w", padx=20)

    def submit():
      name = name_entry.get().strip()
      phone = phone_entry.get().strip()
      category = category_var.get()

      if not name or not phone:
        messagebox.showerror("Error", "All fields are required")
        return

      table_id = get_available_table(category)

      if table_id is None:
        messagebox.showinfo(
          "Unavailable",
          f"Sorry, no {category} tables are available."
        )
        return

      # Create customer, reserve table, create order
      customer_id = add_customer(name, phone)
      mark_table_unavailable(table_id)
      order_id = create_order(customer_id, table_id)

      # Update shared state
      self.app.state.current_customer_id = customer_id
      self.app.state.current_table_id = table_id
      self.app.state.current_order_id = order_id
      self.app.state.current_order_items = []

      win.destroy()

      # Move to Order Page (to be implemented next)
      messagebox.showinfo(
        "Success",
        f"Customer added.\nTable {table_id} allocated."
      )

      self.app.show_frame("OrderFrame")  # placeholder

    tk.Button(win, text="Proceed to Order", command=submit).pack(pady=20)


  def open_analytics(self):
    print("Analytics – to be implemented")

  def load_orders(self):
    self.tree.delete(*self.tree.get_children())

    for order in get_all_orders():
      order_id, customer_id, table_id, category, status = order

      action_text = "Checkout" if status == "IN_PROGRESS" else "Remove"

      self.tree.insert(
        "",
        "end",
        values=(
          customer_id,
          table_id,
          category,
          status,
          "View",
          action_text
        ),
        tags=(order_id, table_id, status)
      )
  
  def on_row_action(self, event):
    selected = self.tree.selection()
    if not selected:
      return

    item = self.tree.item(selected[0])
    values = item["values"]
    tags = item["tags"]

    order_id = tags[0]
    table_id = tags[1]
    status = tags[2]

    column = self.tree.identify_column(event.x)

    # Column 5 = Order Details
    if column == "#5":
      self.show_order_details(order_id)

    # Column 6 = Checkout / Remove
    elif column == "#6":
      if status == "IN_PROGRESS":
        self.checkout_order(order_id, table_id)
      else:
        confirm = messagebox.askyesno(
          "Remove Order",
          "Remove this completed order from the dashboard?"
        )
        if confirm:
          hide_order(order_id)
          self.load_orders()


  def show_order_details(self, order_id):
    win = tk.Toplevel(self)
    win.title("Order Details")
    win.geometry("500x400")
    win.grab_set()

    tree = ttk.Treeview(
      win,
      columns=("name", "price", "qty", "subtotal"),
      show="headings"
    )

    tree.heading("name", text="Item")
    tree.heading("price", text="Price")
    tree.heading("qty", text="Qty")
    tree.heading("subtotal", text="Subtotal")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    total = 0
    for item in get_order_items(order_id):
      name, price, qty, subtotal = item
      total += subtotal
      tree.insert("", "end", values=item)

    tk.Label(
      win,
      text=f"Total: ₹{total}",
      font=("Arial", 12, "bold")
    ).pack(pady=10)

  def checkout_order(self, order_id, table_id):
    confirm = messagebox.askyesno(
      "Checkout",
      "Proceed to checkout?"
    )
    if not confirm:
      return

    self.app.state.current_order_id = order_id
    self.app.state.current_table_id = table_id
    self.app.show_frame("BillingFrame")


    messagebox.showinfo("Success", "Order completed")
    self.load_orders()

  def open_analytics(self):
    win = tk.Toplevel(self)
    win.title("Analytics")
    win.geometry("400x400")
    win.grab_set()

    def reset_all():
      confirm = messagebox.askyesno(
        "Reset Database",
        "This will delete ALL orders and customers.\nAre you sure?"
      )
      if confirm:
        reset_database()
        messagebox.showinfo("Reset", "Database has been reset.")
        self.load_orders()
        win.destroy()

    from db import get_total_revenue, get_item_sales

    tk.Label(
      win,
      text=f"Total Revenue: ₹{get_total_revenue()}",
      font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Button(
      win,
      text="Reset Database",
      fg="white",
      bg="red",
      command=reset_all
    ).pack(pady=10)


    tree = ttk.Treeview(
      win,
      columns=("item", "qty"),
      show="headings"
    )

    tree.heading("item", text="Item")
    tree.heading("qty", text="Quantity Sold")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for row in get_item_sales():
      tree.insert("", "end", values=row)

  