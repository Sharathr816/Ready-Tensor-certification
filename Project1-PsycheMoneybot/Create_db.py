from config import collection, embed_model
from utils import clean_text

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# step 1: setup datasources in Data/

#step2: set up chroma database and embedding functions(in config.py)

#step 3: load docs and split them into chunks
def load_docs(DATA_PATH):
    docs = []
    try:
        loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load() #object len will be equal to no of pages in all pdfs(contains page content and metadata
        for content in documents:
            docs.append(content)
    except Exception as e:
        print(e)
    return chunking(docs)

def chunking(book_contents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, #each chunk size
        chunk_overlap=200,  # Overlap to preserve context(means next chunk repeats content of previous chunk(here it is 200 chars)
        separators=["\n\n", "\n", ". ", " ", ""] # where to split as chunks
    )

    chunks = text_splitter.split_documents(book_contents)

    chunk_data = []
    for i, chunk in enumerate(chunks):
        chunk_data.append(chunk)
    return chunk_data


# step4: store chunks in db
def store_chunks_inChroma(chunk_with_meta):
    # Clear existing data
    try:
        ids = collection.get()["ids"]
        print("collection has ",len(collection.get()["ids"]), " entries")
        print("Clearing existing collection data...")
        collection.delete(ids=ids)  # Delete all existing documents(cause code reruns cause duplicates addition)
        print("Cleared")
        print("collection has ",len(collection.get()["ids"]), " entries\n")
    except Exception as e:
        print(f"Collection was empty or error clearing: {e}")

    # Clean and filter chunks
    chunk_contents = []
    metas = []

    for content in chunk_with_meta:
        if content.page_content and isinstance(content.page_content, str) and content.page_content.strip():
            text = clean_text(content.page_content) # to avoid error during tokenization
            chunk_contents.append(text.strip())
            metas.append({'title':content.metadata["title"]})

    if not chunk_contents:
        print("No valid chunks to embed")
        return False

    print("Started embedding...")
    embeddings = embed_model.embed_documents(chunk_contents)
    ids = [f"doc{id}" for id in range(1, len(chunk_contents) + 1)]
    print("embeddings done.")

    print("adding to collection...")
    collection.add(
        embeddings=embeddings,
        documents=chunk_contents,
        metadatas=metas,
        ids=ids
    )
    print("added to collection")
    return True



chunk_data = load_docs("Data/Money")
flag = store_chunks_inChroma(chunk_data)
if flag:
    print("Database successfully created.")
