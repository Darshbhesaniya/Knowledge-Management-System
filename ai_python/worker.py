import asyncio
import os

from bullmq import Worker
from minio import Minio

from langchain_community.document_loaders import PyPDFLoader,UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "kms_collection"

REDIS_URL = "redis://localhost:6379"
QUEUE_NAME = "document-processing-queue"


minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Qdrant  

qdrant_client = QdrantClient(url=QDRANT_URL)

VECTOR_SIZE = 1536

try:
    qdrant_client.get_collection(COLLECTION_NAME)
    print(f"qudrant Collection {COLLECTION_NAME} is already present ")
except Exception:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"Collection {COLLECTION_NAME} created Successfully")


#  OpenAI Embeddings

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
print("OpenAI embedding model is Ready!! ")

# Process document 

async def process_pdf_job(job,job_taken):

    file_name = job.data.get("fileName")

    bucket_name = job.data.get("bucket_name","kms-documents")

    print("-------------- finding... and got a New Job-----------------")

    local_temp_path = f"temp_{file_name}"

    try:
        print("Downloading Document From MineIO......")
        minio_client.fget_object(bucket_name, file_name, local_temp_path)
        print("Downloading successfull ")

        print("Loading text from Document")

        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == '.pdf':
            loader = PyPDFLoader(local_temp_path)
        elif file_extension in ['.ppt','.pptx']:
            loader = UnstructuredPowerPointLoader(local_temp_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    
        documents = loader.load()
        print(f"Toatal pages/slides is {len(documents)}")


        print("Spllting Text from documents")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_documents(documents=documents)
        total_chunks = len(chunks)
        print("Total Chunks is: ",total_chunks)

        BATCH_SIZE = 100
        print(f"Saving to Qdrant in batches of {BATCH_SIZE} chunks...")

        for i in range(0, total_chunks, BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]

            QdrantVectorStore.from_documents(
                documents=batch,
                embedding=embeddings_model,
                url=QDRANT_URL,
                collection_name=COLLECTION_NAME,
            )

            processed_count = min(i + BATCH_SIZE, total_chunks)
            print(f"Saved {processed_count}/{total_chunks} in Qdrant ")

            if processed_count < total_chunks:
                await asyncio.sleep(2)
        print(f"✅ Successfully store data of {file_name} in Qdrant")

    except Exception as error:
        print(f"❌ Error During Processing {file_name}",error)
        raise error

    finally:
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)
            print(f"Deleted Local temp file: {local_temp_path}")

async def main():
    print(f"Python worker is Active... wait for the New PDF(stop: CTRL+C)")

    worker = Worker(
        QUEUE_NAME,
        process_pdf_job,
        {"connection": REDIS_URL, "concurrency":1}
    )

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())



#   .\.venv\Scripts\Activate.ps1
#   uv run worker.py