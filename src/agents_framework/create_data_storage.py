from langchain_community.document_loaders import JSONLoader

def process_data(self, file_path):
    loader = JSONLoader(
        file_path=file_path,
        jq_schema='.Content',
        text_content=False,
        json_lines=True)
    documents = loader.load()
