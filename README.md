# 🗳️ Ranked Choice Voting (RCV) Simulator

[![Deploy on Railway](https://railway.app/button.svg)](https://web-production-d16ce.up.railway.app/)

A full-stack web application that implements a secure and user-friendly Ranked Choice Voting system. Built with Python Flask, SQLAlchemy, and modern frontend technologies, this application demonstrates a real-world implementation of alternative voting systems with a focus on usability and data integrity.

> 🚀 [Live Demo](https://web-production-d16ce.up.railway.app/)

## 🚀 Key Features

### Voter Experience
- 🌟 Interactive, mobile-responsive voting interface
- 🎯 Drag-and-drop or select-based candidate ranking
- 📝 Optional preference selection (only 1st choice required)
- ✅ Real-time form validation and error handling
- 📨 Instant vote confirmation with detailed receipt
- 📱 Progressive Web App (PWA) ready

### Administrative Tools
- 🔐 Secure admin authentication with role-based access
- 📊 Real-time analytics dashboard with interactive charts
- 📥 Export vote data in CSV and JSON formats
- 📈 Voting trend analysis and statistics
- 👥 Voter activity monitoring
- 🔍 Audit log for all administrative actions

### Technical Highlights
- 🛡️ Secure session management with Flask-Login
- 🗃️ SQLite database with SQLAlchemy ORM
- 📈 Chart.js for interactive data visualization
- 🎨 Modern UI with responsive design
- 🔄 Asynchronous data loading for better performance
- 🔒 CSRF protection and input sanitization

## 🛠️ Tech Stack

### Backend
- **Framework**: Python Flask
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **API**: RESTful endpoints

### Frontend
- **Templating**: Jinja2
- **Styling**: Custom CSS with responsive design
- **Charts**: Chart.js
- **Icons**: Font Awesome

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone [your-repo-url]
   cd rcv-simulator
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

7. **Access the application**
   - Voter Portal: http://localhost:3000
   - Admin Dashboard: http://localhost:3000/admin
     - Default credentials: admin/admin123 (change in production!)

## 📊 Project Structure

```
rcv-simulator/
├── app/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── routes.py          # Application routes
│   └── utils.py           # Helper functions
├── instance/              # Database and instance files
├── migrations/            # Database migrations
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── templates/             # HTML templates
│   ├── admin/            # Admin interface templates
│   └── auth/             # Authentication templates
├── tests/                 # Test files
├── .env.example          # Example environment variables
├── config.py             # Configuration settings
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

