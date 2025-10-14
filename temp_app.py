import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------
# 1️⃣  MySQL Database Setup
# ---------------------------
db_user = "root"
db_pass = "Roopesh2004"
db_host = "localhost"
db_name = "medical"

# SQLAlchemy connection string for MySQL
engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}")

Base = declarative_base()

class Condition(Base):
    __tablename__ = "conditions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    symptoms = Column(Text)
    recommendations = Column(Text)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ---------------------------
# 2️⃣  Scraping Logic
# ---------------------------

def scrape_condition_links():
    """Get list of condition URLs from NHS conditions page"""
    url = "https://www.nhs.uk/conditions/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    links = []
    for a in soup.select("ul.nhsuk-list a"):
        href = a.get("href")
        if href and href.startswith("/conditions/"):
            links.append("https://www.nhs.uk" + href)
    return list(set(links))  # unique links

def scrape_condition_page(url):
    """Scrape name, symptoms, and treatment/recommendations from a condition page"""
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    condition_name = soup.find("h1").get_text(strip=True)

    sections = soup.find_all("section")
    symptoms_text, recommendations_text = "", ""

    for sec in sections:
        heading = sec.find(["h2", "h3"])
        if not heading:
            continue
        title = heading.get_text(strip=True).lower()
        if "symptom" in title:
            symptoms_text += sec.get_text(separator=" ", strip=True) + " "
        elif "treatment" in title or "self-care" in title or "prevention" in title:
            recommendations_text += sec.get_text(separator=" ", strip=True) + " "

    return {
        "name": condition_name,
        "symptoms": symptoms_text[:1000],
        "recommendations": recommendations_text[:1000]
    }

# ---------------------------
# 3️⃣  Run Scraping & Store in MySQL
# ---------------------------

def scrape_and_store(limit=10):
    links = scrape_condition_links()
    print(f"Found {len(links)} condition pages. Scraping first {limit}...")

    for i, url in enumerate(links[:limit]):
        try:
            data = scrape_condition_page(url)
            condition = Condition(
                name=data["name"],
                symptoms=data["symptoms"],
                recommendations=data["recommendations"]
            )
            session.add(condition)
            session.commit()
            print(f"[{i+1}] Saved: {data['name']}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    scrape_and_store(limit=10)
