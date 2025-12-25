import os
from glob import glob
from typing import Annotated

import typer
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from typer import secho
from tqdm import tqdm

app = typer.Typer()


def get_blob_client(storage_account: str) -> BlobServiceClient:
    """Create authenticated blob service client using Azure AD."""
    account_url = f"https://{storage_account}.blob.core.windows.net"
    credential = DefaultAzureCredential()

    secho(f"Created Azure blob client at {account_url}.", fg="green")
    return BlobServiceClient(account_url=account_url, credential=credential)


def upload_file(blob_client: BlobServiceClient, container_name: str, file_path: str):
    container_client = blob_client.get_container_client(container_name)

    blob_name = os.path.basename(file_path).lower()
    blob_client = container_client.get_blob_client(blob_name)
    try:
        with open(file_path, "r") as to_upload:
            blob_client.upload_blob(to_upload.read())
            secho(f"    ✓ Uploaded: {blob_name}", fg="blue", bold=True, nl=False)
    except Exception as e:
        secho(f"    ❌ Failed to upload {blob_name}", fg="red", bold=True, nl=False)


def upload_dir(file_dir: str, blob_client: BlobServiceClient, container_name: str):
    file_dir = os.path.abspath(file_dir)
    files = list(
        map(lambda x: os.path.abspath(x), glob(os.path.join(file_dir, "*.md")))
    )

    if len(files) == 0:
        secho(f"No files found at path {file_dir}")
        return

    secho(f"Uploading {len(files)} files to Azure Blob...", fg="green")
    for f in files:
        upload_file(blob_client, container_name, f)
    secho("All files uploaded :)", fg="green")


@app.command()
def main(
    file_dir: Annotated[
        str, typer.Argument(help="The directory where the markdown files are stored.")
    ],
    container_name: Annotated[str, typer.Argument(envvar="CONTAINER_NAME")],
    storage_account: Annotated[str, typer.Argument(envvar="STORAGE_ACCOUNT")],
):
    blob_client = get_blob_client(storage_account)
    upload_dir(file_dir, blob_client, container_name)


if __name__ == "__main__":
    app()
