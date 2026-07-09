import tkinter as tk
from tkinter import messagebox
from db import complete_order, release_table


class CheckoutFrame(tk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app

    tk.Label(
      self,
      text="Payment",
      font=("Arial", 18, "bold")
    ).pack(pady=20)

    self.method = tk.StringVar(value="Cash")

    for m in ["Cash", "Card", "UPI / NEFT"]:
      tk.Radiobutton(
        self,
        text=m,
        variable=self.method,
        value=m
      ).pack(anchor="w", padx=40)

    tk.Button(
      self,
      text="Pay",
      width=15,
      command=self.pay
    ).pack(pady=30)

  def pay(self):
    complete_order(self.app.state.current_order_id)
    release_table(self.app.state.current_table_id)

    messagebox.showinfo(
      "Thank You",
      "Payment successful.\nThank you for dining with us!"
    )

    self.app.show_frame("DashboardFrame")
