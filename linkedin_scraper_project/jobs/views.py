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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

@api_view(['GET', 'POST'])
def job_create_list(request):
    if request.method == 'GET':
        return JobListAPIView.as_view()(request._request)
    elif request.method == 'POST':
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def job_update_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'PUT':
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        job.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)

class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class JobListAPIView(ListAPIView):
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobSerializer
    pagination_class = JobPagination

async def human_scroll(page, duration=6):
    start = time.time()
    while time.time() - start < duration:
        await page.mouse.wheel(0, random.randint(300, 600))
        await asyncio.sleep(random.uniform(1, 1.5))

@sync_to_async
def save_job_to_db(job_data):
    Job.objects.create(**job_data)

def parse_time_posted(time_str):
    try:
        time_str = time_str.lower()
        if "hour" in time_str or "minute" in time_str:
            post_date = datetime.now()
        elif "day" in time_str:
            days_ago = int(time_str.split()[0])
            post_date = datetime.now() - timedelta(days=days_ago)
        else:
            return time_str
        return post_date.strftime("%d %B")
    except Exception as e:
        print("⚠️ Error parsing time_posted:", e)
        return time_str

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
            if any(heading in line.lower() for heading in ["about the company", "job details", "qualifications", "skills", "education"]):
                break
            extracted.append(line.strip())
        return "\n".join([line for line in extracted if line])
    except Exception as e:
        print("⚠️ Error extracting 'About the job':", e)
        return "Error parsing description."

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
                    await job.scroll_into_view_if_needed()
                    await job.click()
                    await asyncio.sleep(random.uniform(3, 4))

                    title = (await page.locator("h1.t-24").text_content() or "Unknown").strip()
                    if title in scraped_titles:
                        continue
                    scraped_titles.add(title)

                    company = (await page.locator("div.job-details-jobs-unified-top-card__company-name a").text_content() or "Unknown").strip()
                    meta_info = (await page.locator("div.job-details-jobs-unified-top-card__primary-description-container span").nth(0).text_content() or "Unknown").strip()

                    parts = [p.strip() for p in meta_info.split("\u00b7")]
                    location = parts[0] if len(parts) > 0 else "Unknown"
                    raw_time_posted = parts[1] if len(parts) > 1 else "Unknown"
                    time_posted = parse_time_posted(raw_time_posted)

                    if await page.locator("button.show-more-less-html__button").is_visible():
                        await page.locator("button.show-more-less-html__button").click()
                        await page.wait_for_timeout(1500)

                    try:
                        description_html = await page.locator("div.show-more-less-html__markup").inner_html()
                    except:
                        description_html = await page.locator("div.jobs-description-content__text--stretch").inner_html()

                    soup = BeautifulSoup(description_html, "html.parser")
                    about_heading = soup.find('h2', string=lambda s: s and "about the job" in s.lower())
                    if about_heading:
                        mt4_div = about_heading.find_next('div', class_='mt4')
                        description = mt4_div.get_text(separator="\n", strip=True) if mt4_div else extract_about_the_job(soup.get_text(separator="\n"))
                    else:
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

def trigger_scraper(request):
    try:
        result = async_to_sync(scrape_linkedin_jobs)()
        return JsonResponse({"message": "✅ Scraping completed", "jobs_scraped": result["scraped"]})
    except Exception as e:
        return JsonResponse({"error": str(e)})

def homepage(request):
    return HttpResponse("""
        <h1>LinkedIn Job Scraper API</h1>
        <p>Hit <code>/scrape/</code> to scrape Python Developer jobs from LinkedIn.</p>
    """)
