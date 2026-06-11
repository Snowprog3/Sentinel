#!/bin/bash

set -e

cd ~/projects/sentinel
docker compose run --rm parser bash -c "cd /app/src/bookstore && scrapy crawl books_detail"
