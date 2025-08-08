from django.http import JsonResponse, HttpResponse
from .models import Job
import asyncio
import json
import time
import random
from datetime import date, datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from asgiref.sync import sync_to_async, async_to_sync
import re
from bs4 import BeautifulSoup
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .serializers import JobSerializer


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class JobListAPIView(ListAPIView):
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobSerializer
    pagination_class = JobPagination

# Human-like scroll
async def human_scroll(page, duration=6):
    start = time.time()
    while time.time() - start < duration:
        await page.mouse.wheel(0, random.randint(300, 600))
        await asyncio.sleep(random.uniform(1, 1.5))

# Save job to DB
@sync_to_async
def save_job_to_db(job_data):
    Job.objects.create(**job_data)

# Convert '2 days ago' to date like '3 August'
def parse_time_posted(time_str):
    try:
        time_str = time_str.lower()
        if "hour" in time_str or "minute" in time_str:
            post_date = datetime.now()
            return post_date.strftime("%#d %B")  # Windows compatible
        if "day" in time_str:
            days_ago = int(time_str.split()[0])
            if 1 <= days_ago <= 6:
                post_date = datetime.now() - timedelta(days=days_ago)
                return post_date.strftime("%#d %B")
        return time_str
    except Exception as e:
        print("⚠️ Error parsing time_posted:", e)
        return time_str

# Extract only "About the job" section from full description
def extract_about_the_job(text):
    try:
        lines = text.splitlines()
        start_idx = -1
        for i, line in enumerate(lines):
            if "about the job" in line.strip().lower():
                start_idx = i
                break
        if start_idx == -1:
            return "About the job section not found."
        extracted = []
        for line in lines[start_idx:]:
            if any(heading in line.lower() for heading in [
                "about the company", "job details", "qualifications", "skills", "education"]):
                break
            extracted.append(line.strip())
        return "\n".join([line for line in extracted if line])
    except Exception as e:
        print("⚠️ Error extracting 'About the job':", e)
        return "Error parsing description."

# Scraper Logic
async def scrape_linkedin_jobs():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False, slow_mo=80)
        context = await browser.new_context()

        try:
            with open("cookies.json", "r") as f:
                cookies = json.load(f)["cookies"]
            await context.add_cookies(cookies)
        except Exception as e:
            print("❌ Failed to load cookies:", e)
            await browser.close()
            return {"scraped": 0, "error": "Invalid cookies"}

        page = await context.new_page()
        try:
            await page.goto("https://www.linkedin.com/jobs/search/?keywords=python%20developer", wait_until="load", timeout=60000)
        except PlaywrightTimeoutError:
            await asyncio.sleep(3)
            try:
                await page.goto("https://www.linkedin.com/jobs/search/?keywords=python%20developer", wait_until="load", timeout=60000)
            except Exception as e:
                await browser.close()
                return {"scraped": 0, "error": f"Failed to load page: {e}"}
        await asyncio.sleep(5)
        scraped_titles = set()
        total_scraped = 0

        while total_scraped < 100:
            await human_scroll(page)
            try:
                await page.wait_for_selector(".job-card-container--clickable", timeout=15000)
                job_cards = await page.locator(".job-card-container--clickable").all()
            except PlaywrightTimeoutError:
                print("⚠️ Timeout: Job cards not found")
                break

            for job in job_cards:
                if total_scraped >= 100:
                    break
                try:
                    await job.click()
                    await asyncio.sleep(random.uniform(3, 4))

                    title = await page.locator("h1.t-24").text_content() or "Unknown"
                    title = title.strip()
                    if title in scraped_titles:
                        continue
                    scraped_titles.add(title)

                    company = await page.locator("div.job-details-jobs-unified-top-card__company-name a").text_content() or "Unknown"
                    company = company.strip()

                    meta_info = await page.locator("div.job-details-jobs-unified-top-card__primary-description-container span").nth(0).text_content() or "Unknown"
                    meta_info = meta_info.strip()
                    parts = [p.strip() for p in meta_info.split("\u00b7")]
                    location = parts[0] if len(parts) > 0 else "Unknown"
                    raw_time_posted = parts[1] if len(parts) > 1 else "Unknown"
                    time_posted = parse_time_posted(raw_time_posted)

                    see_more_button = page.locator("button.show-more-less-html__button")
                    if await see_more_button.is_visible():
                        await see_more_button.click()
                        await page.wait_for_timeout(1500)

                    try:
                        description_html = await page.locator("div.show-more-less-html__markup").inner_html()
                    except:
                        description_html = await page.locator("div.jobs-description-content__text--stretch").inner_html()

                    soup = BeautifulSoup(description_html, "html.parser")

                    # Try to find the heading and the specific div.mt4 after it
                    about_heading = soup.find('h2', string=lambda s: s and "about the job" in s.lower())
                    if about_heading:
                        mt4_div = about_heading.find_next('div', class_='mt4')
                        if mt4_div:
                            # Get clean text inside the mt4 div
                            description = mt4_div.get_text(separator="\n", strip=True)
                        else:
                            # fallback to full text parsing if mt4 div not found
                            description = extract_about_the_job(soup.get_text(separator="\n"))
                    else:
                        # fallback if heading not found
                        description = extract_about_the_job(soup.get_text(separator="\n"))

                        description = description.strip() 
                          
                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "time_posted": time_posted,
                        "description": description,
                        "scraped_date": date.today(),
                        "scraped_time": datetime.now().time(),
                    }

                    await save_job_to_db(job_data)
                    total_scraped += 1
                    print(f"✅ Scraped {total_scraped}: {title} @ {company} - {time_posted}")

                except Exception as e:
                    print(f"⚠️ Job scrape failed: {e}")
                    continue

            try:
                next_btn = page.locator("button.jobs-search-pagination__button--next")
                if await next_btn.is_enabled():
                    await next_btn.click()
                    await asyncio.sleep(random.uniform(4, 6))
                else:
                    break
            except Exception as e:
                print("⚠️ Pagination failed:", e)
                break

        await browser.close()
        return {"scraped": total_scraped}

# View to trigger scraping
def trigger_scraper(request):
    try:
        result = async_to_sync(scrape_linkedin_jobs)()
        return JsonResponse({"message": "✅ Scraping completed", "jobs_scraped": result["scraped"]})
    except Exception as e:
        return JsonResponse({"error": str(e)})

# Homepage view
def homepage(request):
    return HttpResponse("""
        <h1>LinkedIn Job Scraper API</h1>
        <p>Hit <code>/scrape/</code> to scrape Python Developer jobs from LinkedIn.</p>
    """)
