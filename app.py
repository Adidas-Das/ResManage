# app.py

import tkinter as tk
from frames.start import StartFrame
from frames.dashboard import DashboardFrame
from frames.order import OrderFrame
from frames.billing import BillingFrame
from frames.checkout import CheckoutFrame
from state import AppState


class RestaurantApp(tk.Tk):
  def __init__(self):
    super().__init__()

    self.title("Restaurant Management System")
    self.geometry("1100x650")
    self.resizable(False, False)


    self.state = AppState()

    container = tk.Frame(self)
    container.pack(fill="both", expand=True)

    self.frames = {}

    for FrameClass in (StartFrame, DashboardFrame, OrderFrame, BillingFrame, CheckoutFrame):
      frame = FrameClass(parent=container, app=self)
      self.frames[FrameClass.__name__] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame("StartFrame")

  def show_frame(self, name):
    frame = self.frames[name]
    frame.tkraise()


if __name__ == "__main__":
  app = RestaurantApp()
  app.mainloop()
