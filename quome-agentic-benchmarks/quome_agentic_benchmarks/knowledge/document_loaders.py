from langchain_community.document_loaders import RecursiveUrlLoader


# https://python.langchain.com/v0.2/docs/integrations/document_loaders/recursive_url/
# https://api.python.langchain.com/en/latest/document_loaders/langchain_community.document_loaders.recursive_url_loader.RecursiveUrlLoader.html
def load_fast_api_docs():
    fast_api_docs_loader = RecursiveUrlLoader(
        "https://fastapi.tiangolo.com/tutorial/"
    )
    iter_docs = fast_api_docs_loader.lazy_load()

    doc = next(iter_docs)
    # TODO - Iterate through docs and index them somewhere, elasticsearch? Vector search tool?
    print(doc)



