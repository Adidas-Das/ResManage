# frames/start.py

import tkinter as tk

class StartFrame(tk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app

    title = tk.Label(
      self,
      text="Welcome to Our Restaurant",
      font=("Arial", 22, "bold")
    )
    title.pack(pady=50)

    subtitle = tk.Label(
      self,
      text="Restaurant Management System",
      font=("Arial", 14)
    )
    subtitle.pack(pady=10)

    start_btn = tk.Button(
      self,
      text="Start",
      width=20,
      height=2,
      command=self.start_app
    )
    start_btn.pack(pady=40)

  def start_app(self):
    self.app.show_frame("DashboardFrame")
    
