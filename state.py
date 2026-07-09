# state.py

class AppState:
  def __init__(self):
    self.current_customer_id = None
    self.current_table_id = None
    self.current_order_id = None
    self.current_order_items = []  # in-memory order before commit
