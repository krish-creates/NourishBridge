## NourishBridge: Connecting Surplus to Success

**NourishBridge** is a localized, technology-driven platform designed to tackle the dual challenges of hospitality food waste and community food insecurity. By acting as a digital intermediary, the system allows verified restaurants to list surplus, high-quality food and connects them with authenticated welfare organizations like orphanages and shelters.

The platform solves the "Last-Mile" logistics problem by integrating a decentralized **"Delivery Hero"** volunteer network, ensuring that food is redistributed safely and efficiently.

---

## 🚀 Core Features

* **Role-Based Access Control (RBAC):** Secure, dedicated dashboards for Admins, Restaurants, Welfare Homes, and Delivery Volunteers.
* **Compliance Audit System:** A "Human-in-the-loop" verification process where Admins audit ISO certificates and government IDs before user activation.
* **Partial Allocation Algorithm:** Intelligent inventory management that allows multiple recipients to claim portions of a single large surplus listing.
* **Live Logistics Tracking:** Real-time task management for volunteers, transitioning requests from "Pending Pickup" to "Delivered."
* **Impact Analytics:** Dynamic visualization of food redistributed and community reach using Matplotlib and Pandas.
* **Incentivized Volunteering:** An NGO-funded digital wallet system that tracks and rewards "Delivery Heroes" for their service.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based reactive web framework)
* **Backend:** Python 3.x
* **Database:** SQLite3 (Relational database for ACID-compliant transactions)
* **Data Processing:** Pandas
* **Visualization:** Matplotlib

---

## 📂 Project Structure

```text
NourishBridge/
├── app.py                # Main Entry Point & Authentication Hub
├── food_hero.db          # SQLite Database (Auto-generated)
├── requirements.txt      # Project Dependencies
├── pages/                # Role-Specific Dashboards
│   ├── 1_Admin.py        # Verification & Analytics
│   ├── 2_Restaurant.py   # Surplus Management
│   ├── 3_Homes.py        # Request & Feed System
│   └── 4_Delivery_Hero.py# Logistics & Wallet
└── docs/                 # Documentation & Images
```

---

## ⚙️ Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/NourishBridge.git
   cd NourishBridge
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

---

## 🔄 System Logic: The Connection

NourishBridge operates on a **State-Transition Model**:

1.  **Surplus Posted:** Restaurant creates a listing (Status: `Available`).
2.  **Request Made:** Welfare Home requests portions (Status: `Pending Approval`).
3.  **Allocation:** Restaurant approves the request. The **Partial Allocation Algorithm** subtracts from inventory and updates the request (Status: `Pending Pickup`).
4.  **Claimed:** A Delivery Hero claims the task (Status: `In Transit`).
5.  **Delivery:** Hero confirms drop-off (Status: `Delivered`). Wallet is credited with ₹80.

---

## 🛡️ Security

* **Session Management:** Uses `st.session_state` to prevent unauthorized page access.
* **Database Integrity:** Parametrized SQL queries are used to prevent SQL Injection attacks.
* **Verification Gate:** Accounts remain locked (`is_approved = 0`) until a manual document audit is performed by the Admin.

---

## 🔮 Future Roadmap

* **Google Maps API Integration:** For automated route optimization and real-time distance tracking.
* **IoT Sensors:** Integrating temperature tracking for high-perishability cooked meals.
* **Automated Notifications:** SMS/WhatsApp alerts for nearby volunteers when a pickup is ready.

---

## 📄 License

This project is developed for educational purposes as part of a Final Year Project.
