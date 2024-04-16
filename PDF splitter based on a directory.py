import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(path, output_folder):
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    with open(path, 'rb') as file:
        pdf = PdfReader(file)

        # Iterate through each page of the PDF
        for page_number in range(len(pdf.pages)):
            # Create a new PDF writer for each page
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf.pages[page_number])

            # Generate the output filename
            filename = os.path.splitext(os.path.basename(path))[0]
            output_filename = f"{filename}_page_{page_number + 1}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            # Write the page to a new PDF file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            print(f'Created: {output_filename}')

# Function to split all PDF files in a folder
def split_all_pdfs_in_folder(folder_path, output_folder):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)
    
    # Iterate through each file in the folder
    for file in files:
        # Check if the file is a PDF
        if file.endswith(".pdf"):
            # Generate the path to the file
            file_path = os.path.join(folder_path, file)
            
            # Split the PDF file
            split_pdf(file_path, output_folder)

# Example usage:
folder_path = 'pdf_folder'  # Replace 'pdf_folder' with the path to your folder
output_folder = 'output'  # Replace 'output' with the desired output folder path
split_all_pdfs_in_folder(folder_path, output_folder)