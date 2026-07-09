import tkinter as tk
from tkinter import ttk, messagebox
from db import get_menu_items, add_order_item


class OrderFrame(tk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app

    title = tk.Label(
      self,
      text="Place Order",
      font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    content = tk.Frame(self)
    content.pack(fill="both", expand=True, padx=20)

    # ---------- MENU TABLE ----------
    menu_frame = tk.LabelFrame(content, text="Menu", width=500)
    menu_frame.pack(side="left", fill="y", padx=10)
    menu_frame.pack_propagate(False)


    self.menu_tree = ttk.Treeview(
      menu_frame,
      columns=("id", "name", "type", "price"),
      show="headings",
      height=15
    )

    # Column headings
    self.menu_tree.heading("id", text="Item ID")
    self.menu_tree.heading("name", text="Item Name")
    self.menu_tree.heading("type", text="Veg / Non-Veg")
    self.menu_tree.heading("price", text="Price")

    # Column widths (IMPORTANT)
    self.menu_tree.column("id", width=50, anchor="center", stretch=False)
    self.menu_tree.column("name", width=140, anchor="w", stretch=False)
    self.menu_tree.column("type", width=120, anchor="center", stretch=False)
    self.menu_tree.column("price", width=80, anchor="e", stretch=False)


    menu_scroll = ttk.Scrollbar(menu_frame, orient="vertical", command=self.menu_tree.yview)
    self.menu_tree.configure(yscrollcommand=menu_scroll.set)

    menu_scroll.pack(side="right", fill="y")
    self.menu_tree.pack(fill="both", expand=True)


    self.load_menu()

    # ---------- ORDER TABLE ----------
    order_frame = tk.LabelFrame(content, text="Current Order", width=400)
    order_frame.pack(side="right", fill="y", padx=10)
    order_frame.pack_propagate(False)


    self.order_tree = ttk.Treeview(
      order_frame,
      columns=("id", "name", "qty", "subtotal"),
      show="headings",
      height=15
    )

    self.order_tree.heading("id", text="Item ID")
    self.order_tree.heading("name", text="Item Name")
    self.order_tree.heading("qty", text="Quantity")
    self.order_tree.heading("subtotal", text="Subtotal")

    self.order_tree.column("id", width=50, anchor="center", stretch=False)
    self.order_tree.column("name", width=140, anchor="w", stretch=False)
    self.order_tree.column("qty", width=80, anchor="center", stretch=False)
    self.order_tree.column("subtotal", width=100, anchor="e", stretch=False)


    order_scroll = ttk.Scrollbar(order_frame, orient="vertical", command=self.order_tree.yview)
    self.order_tree.configure(yscrollcommand=order_scroll.set)

    order_scroll.pack(side="right", fill="y")
    self.order_tree.pack(fill="both", expand=True)


    # ---------- CONTROLS ----------
    controls = tk.Frame(self)
    controls.pack(pady=10)

    tk.Button(
      controls,
      text="Add Item",
      width=15,
      command=self.add_item
    ).pack(side="left", padx=5)

    tk.Button(
      controls,
      text="Modify Order",
      width=15,
      command=self.modify_item
    ).pack(side="left", padx=5)

    tk.Button(
      controls,
      text="Done",
      width=15,
      command=self.finish_order
    ).pack(side="left", padx=5)

  # ---------- LOAD MENU ----------
  def load_menu(self):
    self.menu_tree.delete(*self.menu_tree.get_children())
    for item in get_menu_items():
      self.menu_tree.insert("", "end", values=item)

  # ---------- ADD ITEM ----------
  def add_item(self):
    win = tk.Toplevel(self)
    win.title("Add Item")
    win.geometry("300x200")
    win.grab_set()

    tk.Label(win, text="Item ID").pack(pady=5)
    item_entry = tk.Entry(win)
    item_entry.pack()

    tk.Label(win, text="Quantity").pack(pady=5)
    qty_entry = tk.Entry(win)
    qty_entry.insert(0, "1")
    qty_entry.pack()

    def submit():
      try:
        item_id = int(item_entry.get())
        qty = int(qty_entry.get())
      except ValueError:
        messagebox.showerror("Error", "Invalid input")
        return

      for row in self.menu_tree.get_children():
        values = self.menu_tree.item(row)["values"]
        if values[0] == item_id:
          self.app.state.current_order_items.append({
            "item_id": item_id,
            "name": values[1],
            "price": values[3],
            "quantity": qty
          })
          self.refresh_order_table()
          win.destroy()
          return

      messagebox.showerror("Error", "Item ID not found")

    tk.Button(win, text="Add", command=submit).pack(pady=15)

  # ---------- MODIFY ITEM ----------
  def modify_item(self):
    selected = self.order_tree.selection()
    if not selected:
      messagebox.showinfo("Info", "Select an item to modify")
      return

    index = self.order_tree.index(selected[0])

    win = tk.Toplevel(self)
    win.title("Modify Item")
    win.geometry("300x200")
    win.grab_set()

    tk.Label(win, text="New Quantity").pack(pady=10)
    qty_entry = tk.Entry(win)
    qty_entry.pack()

    def apply():
      try:
        qty = int(qty_entry.get())
      except ValueError:
        return

      if qty <= 0:
        del self.app.state.current_order_items[index]
      else:
        self.app.state.current_order_items[index]["quantity"] = qty

      self.refresh_order_table()
      win.destroy()

    tk.Button(win, text="Apply", command=apply).pack(pady=20)

  # ---------- REFRESH ORDER TABLE ----------
  def refresh_order_table(self):
    self.order_tree.delete(*self.order_tree.get_children())
    for item in self.app.state.current_order_items:
      subtotal = item["price"] * item["quantity"]
      self.order_tree.insert(
        "",
        "end",
        values=(
          item["item_id"],
          item["name"],
          item["quantity"],
          subtotal
        )
      )

  # ---------- FINISH ORDER ----------
  def finish_order(self):
    if not self.app.state.current_order_items:
      messagebox.showinfo("Info", "Order is empty")
      return

    order_id = self.app.state.current_order_id

    for item in self.app.state.current_order_items:
      add_order_item(
        order_id,
        item["item_id"],
        item["quantity"]
      )

    messagebox.showinfo("Success", "Order placed successfully")
    self.app.show_frame("DashboardFrame")
