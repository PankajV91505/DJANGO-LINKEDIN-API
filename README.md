# 🕷️ Django API – LinkedIn Job Scraper (100+ Jobs)

This Django-based API project scrapes **100+ Python Developer** job listings from **LinkedIn** using **Playwright**, and stores them into a **PostgreSQL** database.

The scraping is triggered via a single API endpoint:  
📡 `http://127.0.0.1:8000/scrape/`  
Once this URL is hit, the bot launches a headless browser, scrolls like a human, clicks on each job post, and extracts data—storing it neatly into your database.

---

## ✅ Features

- 🔎 Scrapes 100+ job postings for **Python Developer** roles
- 🧠 Mimics human scrolling and delay to avoid detection
- 🗃️ Saves each job to PostgreSQL (title, company, location, time posted, description, and link)
- 🧪 Scraping is triggered by a **GET request** to `/scrape/`
- 💾 Uses Django ORM for saving to the database
- ⚡ Built with performance and simplicity in mind

---

## 🛠️ Tech Stack

| Layer       | Technology                      |
|-------------|----------------------------------|
| Backend     | Django, Django REST Framework    |
| Scraper     | Playwright (Python)              |
| Database    | PostgreSQL                       |
| Language    | Python 3.x                       |
| Hosting     | Localhost (or deploy as needed)  |

---

## 🗂️ Project Structure

```
linkedin_scraper_project/
│
├── jobs/ # Django app containing scraper logic
│ ├── scraper/ # Playwright-based scraper functions
│ ├── migrations/
│ └── views.py # Endpoint to trigger scraping
│
├── linkedin_scraper_project/ # Django settings and root config
├── manage.py
├── requirements.txt
└── README.md
```


---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/PankajV91505/Django-api-linkedin-scraper.git
cd Django-api-linkedin-scraper
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # For Windows
# source venv/bin/activate  # For Mac/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
### 4. Install Playwright Browsers

```bash
playwright install
```

### 5. Configure PostgreSQL Database
Make sure you have PostgreSQL installed and running. Create a database named `linkedin_scraper` and update the `settings.py` file with your database credentials.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'linkedin_scraper',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Apply Migrations

```bash 
python manage.py makemigrations
python manage.py migrate
``` 

### 7. Start Development Server

```bash
python manage.py runserver
```
