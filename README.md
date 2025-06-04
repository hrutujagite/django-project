# 🗂️ NoteNook

**NoteNook** is a Django-based web application designed to help college students upload, share, and access academic notes seamlessly. It also features an interactive Q&A forum to foster peer-to-peer learning and collaboration. The project is built with modular design, role-based access, and admin control to ensure quality content and secure participation.

---

## 🌐 Live Demo

🚧 **Currently Unreachable** – The website was deployed via [Railway](https://railway.app), but it's temporarily facing downtime.  
🔧 I'm actively working to restore deployment. Meanwhile, you can explore the full source code here.

---

## ✨ Features

- 🔐 **User Registration & Login**
- 📝 **Upload and Manage Notes**
- 📥 **Admin Approval for Notes**
- 💬 **Interactive Q&A Forum**
- 👨‍🏫 **Role-based Access for Students and Admins**
- 📂 **Media Upload Support**
- 📊 **Minimal Admin Dashboard for Managing Users & Content**
- 🧹 **Secure and Clean Codebase with `.env` Support**

---

## 🛠️ Tech Stack

- **Framework:** Django (Python)
- **Database:** PostgreSQL (for production), SQLite (for development)
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Authentication:** Django's built-in auth system
- **Deployment:** Railway
- **Version Control:** Git & GitHub

---

## 📁 Project Structure

NoteNook/
├── core/ # Project settings and URLs
├── notes_app/ # Notes upload & approval logic
├── forum/ # Q&A forum logic
├── templates/ # All HTML templates
├── static/ # Static files like CSS/JS
├── media/ # Uploaded files
├── db.sqlite3 # Development database
├── manage.py # Django CLI utility
├── requirements.txt # Python dependencies
└── .env # Environment variables (not pushed to GitHub)

---

## 🚀 Getting Started (For Local Use)

```bash
git clone https://github.com/hrutujagite/django-project.git
cd django-project

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser to access the app locally.

⚠️ Known Issues
Deployment via Railway is currently down due to configuration issues.

Admin dashboard is kept minimal for testing purposes.

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.
