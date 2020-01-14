from docx import Document

files = ['file1.docx', 'file2.docx']

def combine_word_documents(files):
    merged_document = Document()

    for index, file in enumerate(files):
        sub_doc = Document(file)

        # Don't add a page break if you've reached the last file.
        if index < len(files)-1:
           sub_doc.add_page_break()

        body = sub_doc.element.body
        for element in body:
            merged_document.element.body.append(element)
            
        next = body.getnext() 
        while next is not None:
            for element in next:
                merged_document.element.body.append(element)
            next = next.getnext()

    merged_document.save('merged.docx')

combine_word_documents(files)
