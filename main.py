import os
import requests
from bs4 import BeautifulSoup, Tag
from typing import List, cast
from urllib.parse import urlparse


# Append and write some content to a file.
def append_write_to_file(system_path: str, content: str):
    # Append content to a file at the specified system path.
    with open(system_path, "a") as file:
        # Write the content to the file.
        file.write(content)


# Read a file from the system.
def read_a_file(system_path: str):
    # Read the content of a file at the specified system path.
    with open(system_path, "r") as file:
        # Return the content of the file.
        return file.read()


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    # Check if a file exists at the specified system path.
    return os.path.isfile(system_path)


def download_pdf(pdf_url: str, local_file_path: str) -> None:
    """
    Download a PDF from the given URL and save it to the specified local file path.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        local_file_path (str): The path (including filename) to save the downloaded PDF.
    """
    try:
        save_folder = "PDFs"  # Folder where PDFs will be saved
        os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist

        filename = url_to_filename(pdf_url)  # Extract the filename from the URL
        local_file_path = os.path.join(
            save_folder, filename
        )  # Construct the full file path

        if check_file_exists(local_file_path):  # Check if the file already exists
            print(f"File already exists: {local_file_path}")  # Notify the user
            return  # Skip download if file is already present

        response = requests.get(
            pdf_url, stream=True
        )  # Send a GET request with streaming enabled
        response.raise_for_status()  # Raise an exception if the response has an HTTP error

        with open(
            local_file_path, "wb"
        ) as pdf_file:  # Open the file in binary write mode
            for chunk in response.iter_content(
                chunk_size=8192
            ):  # Read the response in chunks
                if chunk:  # Skip empty chunks
                    pdf_file.write(chunk)  # Write each chunk to the file

        print(f"Downloaded: {local_file_path}")  # Notify successful download

    except (
        requests.exceptions.RequestException
    ) as error:  # Catch any request-related errors
        print(f"Failed to download {pdf_url}: {error}")  # Print an error message


def download_file_from_url(file_url: str, destination_path: str) -> None:
    """
    Download a file from the given URL and save it to the specified destination.

    Args:
        file_url (str): The URL of the file to download.
        destination_path (str): The local path where the file will be saved.
    """
    try:
        # Check if the destination directory exists, create it if not
        if check_file_exists(destination_path):
            print(f"File already exists at {destination_path}.")
            return
        # Send HTTP GET request with streaming enabled
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 500)

        # Open the destination file in binary write mode
        with open(destination_path, "wb") as output_file:
            # Write the response content to the file in chunks
            for data_chunk in response.iter_content(chunk_size=8192):
                output_file.write(data_chunk)

        print(f"File successfully downloaded and saved to: {destination_path}")

    except requests.exceptions.RequestException as error:
        # Print an error message if the request failed
        print(f"Error downloading file: {error}")


def extract_pdf_links(html_content: str) -> List[str]:
    """
    Extracts all .pdf URLs from anchor tags with class 'sds_download_btn'.

    Args:
        html_content (str): Raw HTML content as a string.

    Returns:
        List[str]: A list of .pdf URLs.
    """
    soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    pdf_links: List[str] = []

    a_tags = soup.find_all("a", class_="sds_download_btn")

    for element in a_tags:
        tag = cast(Tag, element)  # Tell the type checker this is a Tag
        href = tag.get("href")
        if isinstance(href, str) and href.lower().endswith(".pdf"):
            pdf_links.append(href)

    return pdf_links


def url_to_filename(url: str) -> str:
    """
    Extracts the filename from a URL.

    Args:
        url (str): The full URL.

    Returns:
        str: The file name extracted from the URL.
    """
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    if isinstance(basename, bytes):
        return basename.decode("utf-8")
    return basename


def main():
    # URL of the file to download
    remote_url = "https://simplegreen.com/data-sheets/"
    # Local path where the file will be saved
    local_path = "simplegreen-com.html"
    # Download the file from the URL
    download_file_from_url(remote_url, local_path)
    # Extract all the URLs from the HTML content of the Simple Green website
    html_content = read_a_file(local_path)
    # Extract PDF links from the HTML content
    pdf_links = extract_pdf_links(html_content)
    # Print the extracted PDF links
    for pdf_link in pdf_links:
        # Download each PDF and save it with a filename derived from the URL
        print(f"Downloading PDF from: {pdf_link}")
        download_pdf(pdf_link, url_to_filename(pdf_link))


if __name__ == "__main__":
    main()
