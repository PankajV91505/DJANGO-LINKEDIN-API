from django.http import JsonResponse, HttpResponse
from .models import Job
import asyncio
import json
import time
from playwright.async_api import async_playwright, TimeoutError
from asgiref.sync import sync_to_async, async_to_sync

# Human-like scrolling
async def human_scroll(page, duration=5):
    start = time.time()
    while time.time() - start < duration:
        await page.mouse.wheel(0, 500)
        await asyncio.sleep(1)

# Save job data to DB
@sync_to_async
def save_job_to_db(job_data):
    Job.objects.create(**job_data)

# Main scraper function
async def scrape_linkedin_jobs():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)  # set headless=False for debugging
        context = await browser.new_context()

        # Load cookies
        with open("cookies.json", "r") as f:
            cookies = json.load(f)["cookies"]
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        await page.goto("https://www.linkedin.com/jobs/search/?keywords=python%20developer")
        await asyncio.sleep(5)

        scraped_jobs = []
        total_scraped = 0

        while total_scraped < 100:
            await human_scroll(page, duration=6)

            try:
                await page.wait_for_selector(".job-card-container--clickable", timeout=15000)
                job_cards = await page.locator(".job-card-container--clickable").all()
            except TimeoutError:
                print("⚠️ Timeout: No job cards found.")
                break

            for job in job_cards:
                if total_scraped >= 100:
                    break
                try:
                    await job.click()
                    await asyncio.sleep(3)

                    # Extract job data with error handling
                    try:
                        title = await page.locator("h1.t-24").text_content()
                    except:
                        title = "Unknown"

                    try:
                        company = await page.locator("div.job-details-jobs-unified-top-card__company-name a").text_content()
                    except:
                        company = "Unknown"

                    try:
                        location = await page.locator("div.job-details-jobs-unified-top-card__primary-description-container span").nth(0).text_content()
                    except:
                        location = "Unknown"

                    try:
                        time_posted = await page.locator("div.job-details-jobs-unified-top-card__primary-description-container span").nth(2).text_content()
                    except:
                        time_posted = "Unknown"

                    try:
                        description = await page.locator("div.jobs-description-content__text--stretch").text_content()
                    except:
                        description = "No description found."

                    job_data = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "time_posted": time_posted.strip(),
                        "description": description.strip()
                    }

                    await save_job_to_db(job_data)
                    scraped_jobs.append(job_data)
                    total_scraped += 1
                    print(f"✅ Scraped {total_scraped}: {title} at {company}")

                except TimeoutError as e:
                    print("⚠️ Timeout while scraping a job:", e)
                except Exception as e:
                    print("⚠️ Error:", e)

            # Next Page
            try:
                next_btn = page.locator("button.jobs-search-pagination__button--next")
                if await next_btn.is_enabled():
                    await next_btn.click()
                    await asyncio.sleep(5)
                else:
                    break
            except:
                break

        await browser.close()
        return scraped_jobs

# Django view to trigger scraping
def trigger_scraper(request):
    try:
        async_to_sync(scrape_linkedin_jobs)()
        return JsonResponse({"message": "✅ Scraping completed and data saved to DB."})
    except Exception as e:
        return JsonResponse({"error": str(e)})

# Homepage route
def homepage(request):
    return HttpResponse("<h1>Welcome to the LinkedIn Scraper API</h1><p>Use <code>/scrape/</code> to start scraping 100+ Python developer jobs and save them to PostgreSQL.</p>")
