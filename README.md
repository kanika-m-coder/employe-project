# AttendPay – Modern Enterprise Employee Attendance & Payroll Management System

A comprehensive Employee Attendance, Leave Management, and Payroll Analysis Platform built with modern web technologies, Core Java, JDBC, MySQL/MariaDB, and Python data visualization.

---

## 🎨 Enterprise SaaS Features
- **Executive Dashboard:** Real-time statistics, monthly attendance trend charts, status distributions, and department breakdowns.
- **Dark Midnight Sidebar:** Intuitive navigation with modern Lucide icons, responsive drawer, and active state indicators.
- **Attendance & Leave Management:** Complete leave requests, multi-level approvals, and daily attendance duty logs.
- **Automated Payroll Engine:** Accurate statutory deductions, allowances, HRA/DA calculation, and itemized printable payslips.
- **Analytics & Reports:** Python-powered attendance distribution and monthly payroll pattern visual charts.

---

## 💻 Tech Stack
- **Backend:** Java 17+ (Built-in `com.sun.net.httpserver`, JDBC)
- **Database:** MySQL 8+ / MariaDB 10.11+
- **Data Analytics:** Python 3.9+ (`pandas`, `matplotlib`, `mysql-connector-python`)
- **Frontend:** Modern Semantic HTML5, Vanilla JavaScript (ES6+), Modern CSS3 Design System with Inter typography and Lucide icons
- **Visualizations:** Chart.js 4.4+ and Matplotlib

---

## ⚙️ Quick Start & Setup

### 1. Requirements
- JDK 17 or later
- MySQL Server / MariaDB
- Python 3.9 or later
- MySQL Connector/J in `lib/` (e.g. `mysql-connector-j-8.4.0.jar`)

### 2. Database Initialization
Create the database and seed the initial sample records:
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/sample_data.sql
```

### 3. Python Requirements
Install dependencies for the analysis engine:
```bash
pip install -r python/requirements.txt
```

### 4. Run with ONE Command in VS Code
Open the VS Code terminal (`Ctrl + \``) and run:
```cmd
.\run.bat
```
*(Or in PowerShell: `.\run.ps1`)*

**What this single command handles automatically:**
1. ✅ Automatically configures Java, MariaDB, and Python paths.
2. ✅ Checks and starts the database server on port 3307.
3. ✅ Verifies and auto-initializes the database schema & sample data if missing.
4. ✅ Automatically opens your browser at **http://localhost:8080**.
5. ✅ Launches the AttendPay Java Web Server.

*(Shortcut in VS Code: Press **`Ctrl + Shift + B`** to run AttendPay instantly!)*

---

## 🔑 Login Credentials

### Administrator Portal:
- **Username:** `admin`
- **Password:** `admin123`

### Employee Portal:
- **Username / Employee ID:** `101` (or any valid Employee ID e.g. `102`–`110`)
- **Password:** `emp123`

---

## 📐 Statutory Payroll Calculation Rules
- **HRA:** 20% of Basic Salary
- **DA:** 10% of Basic Salary
- **PF Deduction:** 12% of Basic Salary
- **Per-Day Pay Rate:** `Basic Salary ÷ Weekdays in Month` (Monday–Friday)
- **Absence Deduction:** `Absent Days × Per-Day Rate` (Full absent day = 1.0 deduction, half day = 0.5 deduction, approved paid leave = 0 deduction)
- **Net Take-Home Pay:** `Gross Pay (Basic + HRA + DA) - Total Deductions (PF + Absence Deduction)`
