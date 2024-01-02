import io
import boto3
from docx import Document


class S3FileLoader:
    def __init__(self, bucket_name):
        """
        Initializes an instance of S3FileLoader with the specified S3 bucket name.

        Parameters:
        - bucket_name (str): The name of the S3 bucket containing the '.docx' files.
        """
        self.bucket_name = bucket_name

    def load_files(self):
        """
        Loads and processes '.docx' files from the specified S3 bucket.

        Returns:
        - list of dict: A list of dictionaries where each dictionary represents a '.docx' file
                        with 'title' as the file name and 'content' as the text content.
        """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)

        files_data = []

        for obj in bucket.objects.all():
            if obj.key.endswith('.docx'):
                buffer = io.BytesIO()
                bucket.download_fileobj(obj.key, buffer)
                doc = Document(buffer)
                file_content = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
                file_data = {
                    'title': obj.key,
                    'content': file_content
                }
                files_data.append(file_data)

        return files_data
    