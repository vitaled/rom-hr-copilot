import io
import hashlib
from concurrent.futures import ProcessPoolExecutor
import uuid
import argparse
import sys
import os

base_path = os.getcwd()
print(base_path)
print(os.path.join(base_path, 'utilities'))
sys.path.insert(0, os.path.join(base_path))

from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.AzureBlobStorageClient import AzureBlobStorageClient



def upload_cv(cv_path, upload_id):

    try:
        client = AzureBlobStorageClient()
        cosmos_db = AzureCosmosDBClient()
        form_client = AzureFormRecognizerClient()

        # Set upload run status to running
        cosmos_db.set_upload_run_running(upload_id)

        with open(cv_path, "rb") as f:
            cv = io.BytesIO(f.read())

            # Compute file hash
            hash_md5 = hashlib.md5()
            hash_md5.update(cv.read())
            file_hash = hash_md5.hexdigest()

            # Load file to Azure Blob Storage
            cv.seek(0)
            client.upload_file(cv, f"{file_hash}.pdf", "resumes", "pdf")

            # Extract text from CV
            cv_text = form_client.analyze_read(cv.getvalue())[0]

            # Load cv to Azure Cosmos DB
            cosmos_db.put_resume({
                "id": file_hash,
                "upload_id": upload_id,
                "name": os.path.basename(cv_path),
                "type": os.path.splitext(cv_path)[1],
                "size": os.path.getsize(cv_path),
                "text": cv_text,
            })
            # Set upload run status to completed
            cosmos_db.set_upload_run_completed(upload_id)

    except Exception as e:
        cosmos_db.set_upload_run_failed(upload_id, str(e))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--folder', type=str, required=True)
    parser.add_argument('--parallelism', type=int, required=True, default=2)

    cosmos_db = AzureCosmosDBClient()

    run_id = str(uuid.uuid4())
    upload_ids = []

    args = parser.parse_args()

    # Get all CVs in folder
    uploaded_cv = []
    uploaded_cv_path = []
    for file in os.listdir(args.folder):
        if file.endswith(".pdf"):
            uploaded_cv.append(file)
            uploaded_cv_path.append(os.path.join(args.folder, file))

    for cv in uploaded_cv:
        upload_id = str(uuid.uuid4())
        upload_ids.append(upload_id)
        # run_ids.append(run_id)
        cosmos_db.create_upload_run(upload_id, run_id, cv)

    with ProcessPoolExecutor(max_workers=2) as exe:
        result = exe.map(upload_cv, uploaded_cv_path, upload_ids)


if __name__ == "__main__":
    main()
