#!/usr/bin/env python
import logging
import random

from bs4 import BeautifulSoup
from locust import HttpLocust, TaskSet, task

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def is_static_file(url):
    return url.startswith("/js")


class HashbashTasks(TaskSet):
    page = "/"
    available_ids = []

    def fetch_static_assets(self, page):
        response = self.client.get(page)
        resource_urls = set()
        soup = BeautifulSoup(response.text, "html.parser")

        for res in soup.find_all(src=True):
            url = res["src"]
            if is_static_file(url):
                logging.debug("Retrieving linked static file: {url}")
                response = self.client.get(url)

    @task(2)
    def home_page_task(self):
        self.fetch_static_assets("/home")

    @task(1)
    def rainbow_table_page_task(self):
        self.fetch_static_assets("/rainbow-tables")

    @task(40)
    def rainbow_table_list(self):
        response = self.client.get("/api/rainbow-table")
        rainbow_tables = response.json()
        HashbashTasks.available_ids = [r["id"] for r in rainbow_tables]

    @task(20)
    def rainbow_table_details(self):
        if len(HashbashTasks.available_ids) == 0:
            LOGGER.info("Still no available rainbow tables to query for")
            return

        table_id = random.choice(HashbashTasks.available_ids)
        response = self.client.get(f"/api/rainbow-table/{table_id}")
        response = self.client.get(f"/api/rainbow-table/{table_id}/search")
        response = self.client.get(f"/api/rainbow-table/{table_id}/searchResults")



class HashbashLocust(HttpLocust):
    task_set = HashbashTasks
