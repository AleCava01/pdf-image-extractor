from flask import Flask, render_template, request, send_file, redirect, url_for
import fitz
import os

def delete_pdfs():
     file_list = os.listdir()
     for file_name in file_list:
        if file_name.lower().endswith('.pdf'):  # Verifica se il file ha estensione .pdf
            try:
                os.remove(file_name)
            except:
                print("error occured on delete, i'll do it later")
def extract_images3(filepath):
    images=[]
    count=0
    doc = fitz.open(filepath) # open a document
    for page_index in range(len(doc)): # iterate over pdf pages
            page = doc[page_index] # get the page
            image_list = page.get_images()		

            for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                xref = img[0] # get the XREF of the image
                smask =img[1]
                width=img[2]
                height=img[3]
                bpc=img[4]
                colorspace=img[5]
                name=img[7]
                filter=img[8]
                print("xref: %s smask: %s, name:%s, filter:%s" % (xref,smask,name,filter))
                if(width>1 | height>1):
                    pix = fitz.Pixmap(doc, xref) # create a Pixmap

                    if(smask != 0):
                        pix = fitz.Pixmap(pix, 0) #create the mask
                        pix_mask = fitz.Pixmap(doc, smask) #create the mask
                        pix = fitz.Pixmap(pix, pix_mask) # create a Pixmap

                    if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                                                
                    pix.save("static/images/page_%s-image_%s.png" % (page_index, image_index))
                    images.append("page_%s-image_%s.png" % (page_index, image_index))
                    count += 1
                    pix = None
    print("PyMuPDF Found %s images" % count)
    return images

def delete_images():
    image_dir = 'static/images'  # Percorso della directory delle immagini
    image_files = os.listdir(image_dir)

    # Elimina ciascun file nella lista
    for file_name in image_files:
        file_path = os.path.join(image_dir, file_name)
        try:
            os.remove(file_path)
        except:
            print("error occured on delete, i'll do it later")
delete_images()
delete_pdfs()
        
app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    delete_images()
    delete_pdfs()
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='Nessun file selezionato')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', message='Nessun file selezionato')
        
        if file.filename.lower().endswith('.pdf'):
            file.save(file.filename)
            images=extract_images3(file.filename)
            return render_template('result.html', images=images)
        else:
            return render_template('index.html', message='Si prega di caricare un file PDF')
    
    return render_template('index.html')

@app.route('/download/<path:filename>', methods=['GET'])
def download_image(filename):
    return send_file(filename, as_attachment=True)


@app.route('/back', methods=['POST'])
def go_back():
    
    return redirect('/')

if __name__ == '__main__':
    app.run()

