FROM python:3.11

WORKDIR /scraping_and_indexing

COPY . /scraping_and_indexing

RUN pip install --no-cache-dir -r requirements.txt

RUN python webdriver_downlaod.py

EXPOSE 80


# Run app.py when the container launches
CMD ["python", "main.py"]
