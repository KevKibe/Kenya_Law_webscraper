import os
from dotenv import load_dotenv
load_dotenv()
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from tqdm.auto import tqdm
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken


class Embedder:

    """
    Embedding and indexing textual data using OpenAI and Pinecone.

    Args:
        index_name (str): The name of the Pinecone index.
        data (list): A list of records containing 'content' and 'title' fields.

    Attributes:
        model_name (str): The name of the OpenAI text embedding model.
        openai_api_key (str): The API key for the OpenAI service.
        embeddings (OpenAIEmbeddings): An instance of the OpenAIEmbeddings class.
        index_name (str): The name of the Pinecone index.
        pinecone_api_key (str): The API key for the Pinecone service.
        pinecone_env (str): The environment for Pinecone.
        index (pinecone.Index): An instance of the Pinecone Index class.
        tokenizer: The tokenizer for text encoding.
        text_splitter (RecursiveCharacterTextSplitter): An instance of RecursiveCharacterTextSplitter.
        batch_limit (int): The maximum number of texts to process in a single batch.
        texts (list): A list to store the processed texts.
        metadatas (list): A list to store metadata associated with each processed text.
        data (list): The input data containing records with 'content' and 'title' fields.
    """

    def __init__(self, index_name, data):

        """
        Initializes the Embedder instance.

        Args:
            index_name (str): The name of the Pinecone index.
            data (list): A list of records containing 'content' and 'title' fields.
        """

        self.model_name = 'text-embedding-ada-002'
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.embeddings = OpenAIEmbeddings(
            model=self.model_name,
            openai_api_key=self.openai_api_key
        )
        self.index_name = index_name
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY') 
        self.pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
        pinecone.init(
            api_key=self.pinecone_api_key,
            environment=self.pinecone_env
        )
        self.index = pinecone.Index(self.index_name)
        self.tokenizer = tiktoken.get_encoding('cl100k_base')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=20,
            length_function=self.tiktoken_len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.batch_limit = 20
        self.texts = []
        self.metadatas = []
        self.data = data

    def tiktoken_len(self, text):

        """
        Calculates the length of a text in tokens using the tiktoken tokenizer.

        Args:
            text (str): The input text.

        Returns:
            int: The number of tokens in the text.
        """

        tokens = self.tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

    def process(self):

        """
        Processes the input data, embeds and indexes the texts using OpenAI and Pinecone.
        """

        for i, record in enumerate(tqdm(self.data)):
            metadata = {
                'content': record['content'],
                'title': record['title']
            }
            record_texts = self.text_splitter.split_text(record['content'])
            record_metadatas = [{
                "chunk": j, "text": text, **metadata
            } for j, text in enumerate(record_texts)]
            self.texts.extend(record_texts)
            self.metadatas.extend(record_metadatas)
            if len(self.texts) >= self.batch_limit:
                ids = [str(uuid4()) for _ in range(len(self.texts))]
                embeds = self.embeddings.embed_documents(self.texts)
                self.index.upsert(vectors=zip(ids, embeds, self.metadatas))
                self.texts = []
                self.metadatas = []

        self.index.describe_index_stats()



