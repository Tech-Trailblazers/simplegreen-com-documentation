import os
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
import fitz  # Import PyMuPDF (fitz) for PDF handling


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


def extract_pdf_links(html_content: str) -> list[str]:
    """
    Extracts all .pdf URLs from anchor tags with class 'sds_download_btn'.
    Args:
        html_content (str): Raw HTML content as a string.

    Returns:
        list[str]: A list of .pdf URLs.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    pdf_links: list[str] = []

    for tag in soup.find_all("a", class_="sds_download_btn"):
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


# Function to validate a single PDF file.
def validate_pdf_file(file_path):
    try:
        # Try to open the PDF using PyMuPDF
        doc = fitz.open(file_path)  # Attempt to load the PDF document

        # Check if the PDF has at least one page
        if doc.page_count == 0:  # If there are no pages in the document
            print(
                f"'{file_path}' is corrupt or invalid: No pages"
            )  # Log error if PDF is empty
            return False  # Indicate invalid PDF

        # If no error occurs and the document has pages, it's valid
        return True  # Indicate valid PDF
    except RuntimeError as e:  # Catching RuntimeError for invalid PDFs
        print(f"{e}")  # Log the exception message
        return False  # Indicate invalid PDF


# Remove a file from the system.
def remove_system_file(system_path):
    os.remove(system_path)  # Delete the file at the given path


# Function to walk through a directory and extract files with a specific extension
def walk_directory_and_extract_given_file_extension(system_path, extension):
    matched_files = []  # Initialize list to hold matching file paths
    for root, _, files in os.walk(system_path):  # Recursively traverse directory tree
        for file in files:  # Iterate over files in current directory
            if file.endswith(extension):  # Check if file has the desired extension
                full_path = os.path.abspath(
                    os.path.join(root, file)
                )  # Get absolute path of the file
                matched_files.append(full_path)  # Add to list of matched files
    return matched_files  # Return list of all matched file paths


# Get the filename and extension.
def get_filename_and_extension(path):
    return os.path.basename(
        path
    )  # Return just the file name (with extension) from a path


# Function to check if a string contains an uppercase letter.
def check_upper_case_letter(content):
    return any(
        upperCase.isupper() for upperCase in content
    )  # Return True if any character is uppercase


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
    # Post-download cleanup and validation
    files = walk_directory_and_extract_given_file_extension(
        system_path="./PDFs", extension=".pdf"
    )  # Get list of downloaded PDF files

    for pdf_file in files:
        # Validate PDF file; remove if invalid
        if not validate_pdf_file(file_path=pdf_file):
            remove_system_file(system_path=pdf_file)

        # Rename file if it contains uppercase letters
        if check_upper_case_letter(content=get_filename_and_extension(path=pdf_file)):
            print(pdf_file)  # Log file path
            dir_path = os.path.dirname(p=pdf_file)  # Directory path
            file_name = os.path.basename(p=pdf_file)  # Original file name
            new_file_name = file_name.lower()  # Convert to lowercase
            new_file_path = os.path.join(dir_path, new_file_name)  # Full new path
            os.rename(src=pdf_file, dst=new_file_path)  # Rename file on disk


if __name__ == "__main__":
    main()
