# 📚 StudyScript

> A comprehensive academic management system for students.

🌐 **Live Demo:** https://studyscript.onrender.com/

## ✨ Features

- 🔐 **User Authentication** — Secure registration, login, password hashing and session management.
- 📝 **Assignment Management** — Create, view, complete and delete assignments.
- 🧪 **Exam Countdown** — Track upcoming exams with automatically calculated days remaining.
- ✅ **Daily Tasks** — Manage daily study tasks and mark them as completed.
- 📊 **Progress Tracking** — Visualize daily productivity with a dynamic progress bar.
- 🌙 **Dark Mode** — Persistent Light/Dark theme using LocalStorage.
- 👨‍💼 **Admin Panel** — Role-based access for managing users and platform statistics.
- 📱 **Responsive UI** — Works across desktop, tablet and mobile devices.

## 🛠️ Tech Stack

| Technology       | Usage                       |
| ---------------- | --------------------------- |
| Python 3.12      | Backend                     |
| Flask            | Web framework               |
| HTML5            | Structure                   |
| CSS3             | Styling & responsive design |
| JavaScript       | Frontend interactions       |
| Jinja2           | Templates                   |
| Flask-Login      | Authentication              |
| Flask-SQLAlchemy | ORM                         |
| SQLite           | Database                    |
| Gunicorn         | Production server           |
| Render           | Cloud deployment            |

## 🎯 Project Overview

StudyScript brings **assignments, exams and daily study tasks** into one centralized dashboard. It helps students organize academic work, monitor deadlines and visualize their daily progress.

### Main Workflow

```text
Student
   ↓
Login / Register
   ↓
Dashboard
   ├── Assignments
   ├── Exams & Countdown
   ├── Daily Tasks
   └── Progress Tracking
```

## 🔒 Security

- Passwords protected using PBKDF2 hashing with salt.
- Flask-Login session management.
- Protected user routes.
- User-specific academic data.
- Role-Based Access Control for administrators.

## 🚀 Deployment

StudyScript is deployed on **Render Cloud** using Flask and Gunicorn.

👉 **[Visit the Live Demo](https://studyscript.onrender.com/)**

> The current version uses SQLite. The project report notes scalability limitations with SQLite and possible cold-start delays on the Render free tier.

## 📌 Limitations

- No automated email/SMS/push notifications.
- SQLite is not ideal for large-scale concurrent usage.
- Dark Mode preference is device/browser dependent.
- No PDF/Excel data export.
- No Multi-Factor Authentication.
- No offline mode.

## 🔮 Future Enhancements

- 🤖 AI-based study scheduling
- 👥 Collaborative study rooms
- 📱 Android/iOS application
- 🔔 Push and email notifications
- 🗄️ PostgreSQL migration
- 📄 PDF/Excel export
- 🎓 University API integration

## 👩‍💻 Developer

**Vaishnavi Nivrutti Gadade**

---

⭐ **StudyScript — Plan your work. Track your progress. Stay ahead of deadlines.**
