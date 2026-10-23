import os
from dotenv import load_dotenv
from langchain_openai import (
    OpenAIEmbeddings,
    ChatOpenAI )
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "kms_collection"

print("Qdrant database and OpenAI model are connecting....")

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

qdrant_client = QdrantClient(url=QDRANT_URL)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings_model
)

retriver = vector_store.as_retriever(search_kwargs={"k": 4})

llm = ChatOpenAI(model="gpt-5.6-luna", temperature=0.3)

system_prompt = (
    "You are a helpful and intelligent assistant for a Knowledge Management System."
    "Use the following pieces of retrieved context to answer the user's question."
    "If you don't know the answer or if the answer is not present in the context, "
    "just say 'Sorry, I not have any information for your questions' Do not try to make up an answer. "
    "Keep your answers clear, concise, and well-formatted using bullet points if needed.\n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    ("human","{input}")
])

# Chain
question_answer_chain = create_stuff_documents_chain(llm,prompt)
rag_chain = create_retrieval_chain(retriver, question_answer_chain)

print("System is Ready to Replay Questions\n")


def get_rag_response(question):
    try:
       
        response = rag_chain.invoke({"input": question})
        answer = response["answer"]
        
        # Sources
        unique_sources = set()
        for doc in response["context"]:
            source_path = doc.metadata.get("source", "Unknown")
            file_name = os.path.basename(source_path).replace("temp_", "")
            unique_sources.add(file_name)
            
        return {
            "answer": answer,
            "sources": list(unique_sources)
        }
    except Exception as e:
        return {"answer": f"❌ System Error: {str(e)}", "sources": []}
