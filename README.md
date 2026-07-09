# Restaurant Management System (RMS)

A modular, robust, and session-aware desktop application built entirely in Python. The system streamlines the complete lifecycle of a restaurant's daily operations—handling customer check-ins, automated table reservations, dynamic order staging, graphic receipt generation, secure checkout, and live revenue analytics.

Built using **Tkinter** for the Graphical User Interface (GUI), **SQLite3** for low-latency relational data storage, and the **Pillow (PIL)** library for programmatically rendering physical image-based customer receipts.

---

## 🏗️ Architectural Overview

The application follows a clean, decoupled architectural paradigm separating the layout layer, the transactional database management layer, and the application's runtime session state.

```
                  ┌────────────────────────┐
                  │        app.py          │ (Main Application Window & Core Frame Router)
                  └───────────┬────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
  │   db.py      │    │   state.py   │    │  frames/       │ (UI Views Layer)
  │ (SQLite3     │    │ (Shared Live │    │                │
  │  Persistence)│    │ Session State│    ├── StartFrame   │
  └──────────────┘    └──────────────┘    ├── DashboardFrame
                                          ├── OrderFrame   │
                                          ├── BillingFrame │
                                          └── CheckoutFrame│
```

### 1. Multi-Frame Stacking Architecture (`app.py`)
The application implements a centralized single-window experience. Instead of spawning cluttered, unmanaged independent operational windows, the main window initializes a global root `tk.Frame` container managed via a grid layout. The standalone layout views (`frames/`) are nested into this container simultaneously and toggled dynamically using Tkinter's `.tkraise()` mechanism. This provides a clean desktop interface experience.

### 2. Double-Buffered State Management (`state.py`)
To ensure isolated frames remain decoupled yet capable of sharing transactional data, a global, shared session state model (`AppState`) is passed throughout the lifetime of the application. It acts as an in-memory staging area holding:
* Active context references (`current_customer_id`, `current_table_id`, `current_order_id`).
* An uncommitted transaction buffer (`current_order_items`) serving as a dynamic shopping cart. This enables operators to modify item quantities, append plates, or abort selections without making costly, partial, or unverified writes directly to the hard disk database.

### 3. Data Persistence Layer (`db.py`)
All persistent state transitions are controlled via an embedded SQLite database engine. Relational queries, transactional state updates (`COMMIT`), aggregations, multi-table joins, and table schema alterations are abstracted away into explicit, self-contained functional routines inside `db.py`.

---

## 🗄️ Relational Database Schema

The system operates around five interconnected data entities within the SQLite file structure:

* **`restaurant_tables`**: Stores the layout assets of the restaurant floor. Includes `table_id`, a structural category string (`2-seater`, `4-seater`, `family`), and a boolean state flag (`is_available`).
* **`customers`**: Tracks active dining patrons, archiving their unique auto-incremented `customer_id`, `name`, and `phone` text.
* **`orders`**: The core transactional logger connecting a customer to an assigned table. It tracks lifecycle states via a `status` token (`IN_PROGRESS`, `COMPLETED`) and dashboard display state via a `visible` bitmask toggle.
* **`menu`**: Holds static references for food/beverage offerings including item names, categorization (e.g., Veg/Non-Veg), and base prices.
* **`order_items`**: A dedicated bridge entity breaking down many-to-many associations between an `order` and the `menu`, archiving item ids, specific item quantities, and row-level sub-totals.

---

## 🔄 Core Operational Lifecycle

```
[Start Screen] ➔ [Dashboard: Seat Guest] ➔ [Order Panel: Build Cart] ➔ [Billing Hub: Generate Invoice] ➔ [Checkout Gate: Complete & Release]
```

### Phase 1: Interactive Customer Intake & Table Auto-Allocation
When a guest arrives, administrative staff toggle the intake module from the central dashboard. Upon submitting the guest's profile details and specifying a table type requirement, an intelligent query executes against the database:
```sql
SELECT table_id FROM restaurant_tables 
WHERE category = ? AND is_available = 1 
LIMIT 1;
```
If a record returns, the system immediately reserves it by flipping its availability state (`is_available = 0`), instantiates a unique order ID mapping the customer to that table asset, and flags the session context inside the global state tree.

### Phase 2: Split-Screen Order Assembly
Upon routing to the `OrderFrame`, the view renders an dual-treeview workspace. The left pane provides an explicit look at the live menu table directly pulled from database records, while the right pane visualizes the local cart structure (`current_order_items`). 
* **Modifications**: Operators use modal dialog interfaces to add or scale item quantities. 
* **Batch Commit**: Once the cart matches the physical table selections, clicking the **Done** action executes a batched insertion loop, securely building the transaction records inside `order_items` before gracefully returning the view back to the dashboard.

### Phase 3: The Dashboard Control Center
The `DashboardFrame` coordinates all in-progress restaurant functions. It utilizes an expanded `ttk.Treeview` equipped with specific fixed column weights, column text anchoring, and vertical scroll binding.
Mouse double-clicks are hooked into a coordinate-aware row parsing system:
* **Column 5 Click (Details)**: Triggers an isolated pop-up window fetching individual itemized order receipts via a fast SQL table join query.
* **Column 6 Click (Action)**: Routes active (`IN_PROGRESS`) accounts to the billing phase, or permanently flags old completed orders as invisible (`hide_order`) to clear out UI clutter.

### Phase 4: Dynamic Graphic Receipt Printing Engine
Inside `BillingFrame`, an itemized preview displays calculated totals. When the operator triggers the **Export Bill** routine, the application executes an automated graphics pipeline utilizing the `Pillow` library:
1. It reads the collection of ordered items and determines a custom vertical height matching the absolute volume of text records to prevent truncation.
2. An image object is instantiated (`Image.new("RGB", ...)`) providing a pristine white background canvas.
3. An `ImageDraw` context maps structured geometric formatting: header titles, customer identification data, precise dark underline separators, column alignment offsets, and right-aligned sub-totals.
4. The system outputs a high-resolution, shareable print-ready file onto disk titled dynamically as `bill_order_[ID].png`.

### Phase 5: Secure Checkout & Room Cleanup
The final layout interface (`CheckoutFrame`) registers payments via RadioButton controls supporting Cash, Card, and UPI workflows. Confirming payment completes the transaction loop:
* The order state shifts securely to `COMPLETED`.
* The allocated table is immediately freed up (`is_available = 1`), returning it to the open pool for future customer intake.
* **Live Analytics**: A specialized statistical control frame instantly generates real-time business operational numbers using aggregated query functions (`SUM(m.price * oi.quantity)`) alongside a structural count grouping sales metrics (`GROUP BY m.item_name`) to show exact item popularity over time.

---

## 🛠️ Technology Stack Specifications

* **Language**: Python 3
* **GUI Engine**: Tkinter Core (Native system windows, Grid layout managers, custom Toplevel Modals, and Scrollable Structured Treeviews)
* **Storage Engine**: SQLite3 Relational Database
* **Graphics Suite**: Pillow (PIL) for image canvas construction, dynamic point text drawing, and graphic image receipt output.