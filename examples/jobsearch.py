from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
    IndustryFilters,
)
import telegram_send
import time
import asyncio
import re

seen = set()


def on_data(data: EventData):
    if data not in seen and "selenium" in data.description.casefold():
        seen.add(data)

        # Get the job ID.
        match = re.search(r"/(\d+)/", data.link)
        if not match:
            match = re.search(r"currentJobId=(\d+)", data.link)
        job_id = match.group(1)
        url = f"https://www.linkedin.com/jobs/view/{job_id}/"

        asyncio.run(
            telegram_send.send(
                messages=[
                    f"Title: {data.title}\nCompany: {data.company}\nDate: {data.date}\nLink: {url}"
                ]
            )
        )
        print(
            "[ON_DATA]",
            data.title,
            data.company,
            data.date,
            url,
            len(data.description),
        )


def on_error(error):
    print("[ON_ERROR]", error)


def on_end():
    print("[ON_END]")


scraper = LinkedinScraper(
    chrome_options=None,  # You can pass your custom Chrome options here
    max_workers=1,  # How many threads will be spawn to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1,  # Slow down the scraper to avoid 'Too many requests (429)' errors
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query=query,
        options=QueryOptions(
            locations=["Toronto", "Greater Toronto Area", "Ontario"],
            limit=100,
            skip_promoted_jobs=True,
            filters=QueryFilters(
                company_jobs_url=None,
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.WEEK,
                type=TypeFilters.FULL_TIME,
                experience=None,
                on_site_or_remote=None,
                industry=None,
            ),
        ),
    )
    for query in [
        "Quality Assurance Engineer",
        "QA Engineer",
        "SDET",
        "QA",
        "Quality Assurance",
        "QA Tester",
        "QA Analyst",
        "Quality Engineer",
        "Testing Analyst",
        "Software Test Engineer",
        "Automation Engineer",
        "Test Automation",
        "Test Engineer",
        "Software Tester",
    ]
]

while True:
    scraper.run(queries)
    time.sleep(60)  # sleep 1 minute
    if len(seen) > 1000:
        seen.clear()
