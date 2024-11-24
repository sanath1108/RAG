import PyPDF2
from docx import Document
import io


class DocumentProcessor:
    def __init__(self):
        """Initialize the DocumentProcessor class."""
        print("DocumentProcessor initialized.")

    def extract_text(self, file):
        """
        Extract text from a document (PDF, text, or Word).
        """
        if not file:
            raise ValueError("No file provided.")

        # Handle both file-like objects and raw bytes
        if hasattr(file, 'filename'):
            filename = file.filename
        else:
            filename = "unknown"

        if filename.endswith('.pdf'):
            return self._extract_from_pdf(file)
        elif filename.endswith(('.doc', '.docx')):
            return self._extract_from_word(file)
        elif filename.endswith('.txt'):
            return self._extract_from_text(file)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    def _extract_from_pdf(self, file):
        """
        Extract text from a PDF file object.

        Args:
        file (UploadFile): A file object containing the PDF content.

        Returns:
        str: Extracted text from the PDF file.
        """
        print(f"Extracting text from PDF: {file.filename}")
        text = ""
        try:
            # Reset file pointer to ensure content is readable
            file.file.seek(0)

            # Read the file content and wrap in BytesIO
            pdf_file = io.BytesIO(file.file.read())

            # Check if the file has any content
            if pdf_file.getbuffer().nbytes == 0:
                raise RuntimeError("Uploaded PDF is empty.")

            # Pass the BytesIO object to PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from each page
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:  # Skip empty pages
                    text += page_text + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")
        return text




    def _extract_from_word(self, file):
        """
        Extract text from a Word document file object.
        
        Args:
            file (File): A file object containing the Word document content.
        
        Returns:
            str: Extracted text from the Word document.
        """
        print(f"Extracting text from Word document: {file.filename}")
        text = ""
        try:
            # Open the file as a binary stream
            doc = Document(io.BytesIO(file.read()))
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from Word document: {e}")
        return text

    def _extract_from_text(self, file):
        """
        Extract text from a plain text file object.
        
        Args:
            file (File): A file object containing the plain text content.
        
        Returns:
            str: Extracted text from the text file.
        """
        print(f"Extracting text from text file: {file.filename}")
        try:
            # Read the text directly from the file
            return file.read().decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from text file: {e}")
