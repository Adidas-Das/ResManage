import tkinter as tk
from tkinter import ttk, messagebox
from db import get_order_items
from PIL import Image, ImageDraw, ImageFont
import time


class BillingFrame(tk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app

    title = tk.Label(
      self,
      text="Billing",
      font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    self.bill_frame = tk.Frame(self, bd=2, relief="solid")
    self.bill_frame.pack(padx=20, pady=10)

    # self.build_bill()

    buttons = tk.Frame(self)
    buttons.pack(pady=10)

    tk.Button(
      buttons,
      text="Export Bill",
      width=15,
      command=self.export_bill
    ).pack(side="left", padx=10)

    tk.Button(
      buttons,
      text="Pay",
      width=15,
      command=self.go_to_payment
    ).pack(side="left", padx=10)

  def build_bill(self):
    for w in self.bill_frame.winfo_children():
      w.destroy()

    tk.Label(
      self.bill_frame,
      text="My Restaurant",
      font=("Arial", 16, "bold")
    ).pack()

    tk.Label(
      self.bill_frame,
      text="123 Main Road, City",
      font=("Arial", 10)
    ).pack()

    ttk.Separator(self.bill_frame, orient="horizontal").pack(fill="x", pady=5)

    tree = ttk.Treeview(
      self.bill_frame,
      columns=("name", "price", "qty", "subtotal"),
      show="headings",
      height=10
    )

    tree.heading("name", text="Item")
    tree.heading("price", text="Price")
    tree.heading("qty", text="Qty")
    tree.heading("subtotal", text="Subtotal")

    tree.pack()

    total = 0
    for item in get_order_items(self.app.state.current_order_id):
      tree.insert("", "end", values=item)
      total += item[3]

    ttk.Separator(self.bill_frame, orient="horizontal").pack(fill="x", pady=5)

    tk.Label(
      self.bill_frame,
      text=f"Total: ₹{total}",
      font=("Arial", 12, "bold")
    ).pack(pady=5)

    self.total_amount = total

  def export_bill(self):
    order_id = self.app.state.current_order_id
    items = get_order_items(order_id)

    # Image dimensions
    width = 600
    padding = 20
    line_height = 30

    height = (
      padding * 4 +
      line_height * (len(items) + 8)
    )

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    try:
      font_title = ImageFont.truetype("arial.ttf", 24)
      font_body = ImageFont.truetype("arial.ttf", 16)
    except:
      font_title = ImageFont.load_default()
      font_body = ImageFont.load_default()

    y = padding

    # Header
    draw.text((width//2 - 80, y), "My Restaurant", fill="black", font=font_title)
    y += line_height + 10

    draw.text((padding, y), "123 Main Road, City", fill="black", font=font_body)
    y += line_height

    draw.text((padding, y), f"Order ID: {order_id}", fill="black", font=font_body)
    y += line_height * 2

    # Table header
    draw.text((padding, y), "Item", font=font_body, fill="black")
    draw.text((300, y), "Qty", font=font_body, fill="black")
    draw.text((360, y), "Price", font=font_body, fill="black")
    draw.text((460, y), "Subtotal", font=font_body, fill="black")
    y += line_height

    draw.line((padding, y, width - padding, y), fill="black")
    y += 10

    total = 0

    # Items
    for name, price, qty, subtotal in items:
      draw.text((padding, y), str(name), fill="black", font=font_body)
      draw.text((300, y), str(qty), fill="black", font=font_body)
      draw.text((360, y), f"{price}", fill="black", font=font_body)
      draw.text((460, y), f"{subtotal}", fill="black", font=font_body)
      total += subtotal
      y += line_height

    y += 10
    draw.line((padding, y, width - padding, y), fill="black")
    y += line_height

    draw.text(
      (padding, y),
      f"Total Amount: ₹{total}",
      fill="black",
      font=font_body
    )

    filename = f"bill_order_{order_id}.png"
    img.save(filename)

    messagebox.showinfo(
      "Export Successful",
      f"Bill saved as {filename}"
    )


  def go_to_payment(self):
    self.app.show_frame("CheckoutFrame")

  def tkraise(self, aboveThis=None):
    super().tkraise(aboveThis)
    self.build_bill()
