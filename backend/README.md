# Backend CRUD API (FastAPI + MySQL)

This project is a simple **Backend CRUD application** built using **FastAPI** and **MySQL**.
If you are coming from **Flask**, think of this as the FastAPI version of a REST API
with **better validation, performance, and auto documentation**.

---

## 📌 Tech Stack Used

- **Python 3.8+**
- **FastAPI** – API framework
- **MySQL** – Database
- **Uvicorn** – ASGI server
- **Pydantic** – Data validation
- **JWT (Bearer Token)** – Authentication (Login)

---

## 📌 Project Flow (High Level)

1. User **registers**
2. User **logs in**
3. Backend generates a **JWT access token**
4. Token is used to access **protected APIs** like `/users`

👉 Same concept as Flask, but FastAPI handles many things automatically.

---

## 📌 Prerequisites

Make sure you have the following before running the project:

- Python **3.8 or above**
- MySQL server running on **localhost**
- MySQL user:
  - **username:** `root`
  - **password:** `Shiva@366`

⚠️ If your MySQL credentials are different, update them inside:
