import requests
import logging
import hashlib
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import os
import html
from bs4 import BeautifulSoup

load_dotenv()

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

API_BASE = "https://api.ejobs.ro/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    "Accept": "application/json, text/plain, */*",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.ejobs.ro",
    "Referer": "https://www.ejobs.ro/",
}

session = requests.Session()
session.headers.update(HEADERS)

def clean_html_for_embedding(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    
    # Get plain text
    text = soup.get_text()
    
    # Normalize lines: strip and remove empty lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    
    cleaned_text = "\n".join(lines)
    
    return cleaned_text

def clean_html(raw_text):
    return html.unescape(raw_text).strip()

def get_location_from_coords(lat: float, lng: float) -> dict:
    """Return a dict with city and country based on lat/lng."""
    try:
        params = {"latlng": f"{lat},{lng}", "key": GOOGLE_MAPS_API_KEY}
        response = requests.get(GOOGLE_GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "OK":
            logging.warning(f"Geocoding API status not OK: {data.get('status')}")
            return {"city": "Unknown", "country": "Unknown"}

        components = data["results"][0]["address_components"]

        city = next(
            (c["long_name"] for c in components if "locality" in c["types"]),
            "Unknown"
        )
        country = next(
            (c["long_name"] for c in components if "country" in c["types"]),
            "Unknown"
        )
        return {"city": city, "country": country}

    except Exception as e:
        logging.error(f"Geocoding failed: {e}")
        return {"city": "Unknown", "country": "Unknown"}


def generate_job_id(job: dict) -> str:
    """Create a stable unique hash ID for Elasticsearch `_id`."""
    unique_data = f"{job['company']}|{job['job_title']}|{job['job_url']}"
    return hashlib.sha256(unique_data.encode("utf-8")).hexdigest()


def get_latest_job_id() -> Optional[int]:
    """Fetch the ID of the most recent job posting."""
    try:
        response = session.get(f"{API_BASE}?page=1&pageSize=1&sort=date")
        response.raise_for_status()
        decoded_data = response.content.decode("utf-8", errors="replace")

        latest_job = json.loads(decoded_data)["jobs"][0]
        return latest_job["id"]
    except Exception as e:
        logging.error(f"Failed to get latest job ID: {str(e)}")
        return None
    
def process_job(job_id: int) -> Optional[Dict]:
    """Fetch and process a single job posting."""
    try:
        response = session.get(f"{API_BASE}/{job_id}")
        
        if response.status_code == 404:
            logging.info(f"❌ Job {job_id} not found (404)")
            return None
        response.raise_for_status()

        decoded_data = response.content.decode("utf-8", errors="replace")
        job_data = json.loads(decoded_data)
        
        # Check expiration date
        if expiration_date := job_data.get("expirationDate"):
            exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
            if exp_date < datetime.today():
                logging.info(f"❌ Job {job_id} expired on {expiration_date}")
                return None
        
        # Skip inactive jobs
        if job_data.get("jobType") == "inactive":
            logging.info(f"❌ Skipping inactive job {job_id}")
            return None
        
        # Process description
        details = job_data.get("details", {})

        # Check if any of the meaningful description fields exist and are non-empty
        has_description = any(
            details.get(field) and details.get(field).strip()
            for field in ["jobDescription", "companyDescription", "idealCandidate"]
        )

        if not has_description:
            # Skip this job entirely
            logging.info(f"❌ Job {job_id} has no meaningful description")
            return None
        
        # Clean and extract descriptions
        job_description = clean_html(details.get("jobDescription", ""))
        company_description = clean_html(details.get("companyDescription", ""))
        ideal_candidate = clean_html(details.get("idealCandidate", ""))

        desc_parts = []

        if ideal_candidate:
            desc_parts.append(f"<strong>Ideal Candidate:</strong><br/>{ideal_candidate}")

        if job_description:
            desc_parts.append(f"<strong>Job Description:</strong><br/>{job_description}")

        if company_description:
            desc_parts.append(f"<strong>Company Description:</strong><br/>{company_description}")

        description = "<br/><br/>".join(desc_parts).strip()

        meta_tags = details.get("metaTags")
        if meta_tags:
            meta_tags = meta_tags.strip()
        else:
            meta_tags = None
        
        # Process location data
        location = "Unknown"
        if locations := job_data.get("locations"):
            location_data = locations[0]
            lat = location_data.get("latitude")
            lng = location_data.get("longitude")
            if lat and lng:
                location = get_location_from_coords(lat, lng)
                logging.info(f"Geocoded location for {job_id}: {location}")
        
        return {
            "site_id": job_data["id"],
            "job_title": job_data.get("title"),
            "company": job_data.get("company", {}).get("name"),
            "location": location,
            "description": description,
            "job_url": f"https://www.ejobs.ro/user/locuri-de-munca/{job_data.get('slug')}/{job_id}",
            "expiration_date": expiration_date,
            "meta_tags": meta_tags,
            "date_uploaded": job_data.get("creationDate"),
        }
        
    except Exception as e:
        logging.error(f"❌ Error processing job {job_id}: {str(e)}")
        return None
    

def fetch_new_jobs_from_department(department_id: int, last_indexed_id: Optional[int], max_jobs: int = 300, page_size: int = 40) -> List[Dict]:
    """Fetch only jobs newer than last_indexed_id filtered by department."""
    jobs = []
    page = 1
    while True:
        url = f"https://api.ejobs.ro/jobs?page={page}&pageSize={page_size}&filters.departments={department_id}&sort=date"
        logging.info(f"Fetching jobs from department {department_id}, page {page}")
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()
            page_jobs = data.get("jobs", [])
            if not page_jobs:
                logging.info("No more jobs found on this page.")
                break

            # Filter out jobs already indexed (ID <= last_indexed_id)
            new_jobs_on_page = []
            for job in page_jobs:
                if last_indexed_id is None or job["id"] > last_indexed_id:
                    new_jobs_on_page.append(job)
                else:
                    # Job ID <= last indexed ID means no newer jobs past this
                    logging.info(f"Reached job ID {job['id']} <= last indexed ID {last_indexed_id}, stopping fetch.")
                    break

            jobs.extend(new_jobs_on_page)

            # If found job <= last_indexed_id, stop fetching more pages
            if len(new_jobs_on_page) < len(page_jobs):
                break

            if len(jobs) >= max_jobs:
                jobs = jobs[:max_jobs]
                break

            page += 1

        except Exception as e:
            logging.error(f"Failed to fetch jobs from department {department_id} page {page}: {e}")
            break
    return jobs
