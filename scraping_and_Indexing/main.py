import os
from s3_doc_loader import S3FileLoader
from docx import Document
from embed import Embedder
# from langchain.embeddings import Embedder
from web_scraper import CaseLawScraper

def main():
    # Set up CaseLawDownloader
    base_url = "http://kenyalaw.org/caselaw/cases/advanced_search/page/"
    num_pages = 2
    tmp_directory = '/tmp'
    downloader = CaseLawScraper(base_url, num_pages, tmp_directory)
    downloader.download_cases()
    downloader.note_downloaded_files_s3('kenyalawcasefiles')
    downloader.upload_cases_to_s3('kenyalawcasefiles')
    # Set up S3FileLoader and FileProcessor
    s3_loader = S3FileLoader('kenyalawcasefiles')
    files_data = s3_loader.load_files()
    #embedding and indexing
    embed = Embedder('caselaws', files_data)
    embed.process()

if __name__ == "__main__":
    main()
