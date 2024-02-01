from reportlab.pdfgen import canvas
import json 
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os



def draw_text(c, x1, x2, y1, text, font_size):
    c.setFont("Helvetica", font_size)  
    text_object = c.beginText()
    text_object.setTextOrigin(x1, y1)
    text_object.setFont("Helvetica", font_size)  

    words = text.split()
    line = ""
    lines = 0
    for word in words:
        if c.stringWidth(line + word, "Helvetica", font_size) <= (x2 - x1):
            line += word + " "
        else:
            text_object.textLine(line)
            line = word + " "
            lines += 1
    text_object.textLine(line)
    lines += 1
    c.drawText(text_object)

def draw_figure(c, img_path,x1, y1, x2, y2):
    box_width = x2 - x1
    box_height = y2 - y1

    img = ImageReader(img_path)
    img_width, img_height = img.getSize()
    aspect_ratio = img_width / img_height

    if box_width / aspect_ratio < box_height:
        img_width = box_width
        img_height = img_width / aspect_ratio
    else:
        img_height = box_height
        img_width = img_height * aspect_ratio

    img_x = x1 + (box_width - img_width) / 2
    img_y = y1 + (box_height - img_height) / 2

    c.drawImage(img, img_x, img_y, width=img_width, height=img_height)

def create_pdf_from_json(json_structure,file_name, save_path):
    global y1_start
    work_path = (os.path.dirname(json_structure))
    with open(json_structure, 'r') as json_file:
        json_data = json.load(json_file)

    c = canvas.Canvas(save_path)
    c.setLineWidth(1)
    previous_page = 0
    for element in json_data["elements"]:
        number_of_page = element.get("Page")
        if previous_page != number_of_page:
            c.showPage()
        text = element.get("Text", "")
        bounds = element.get("Bounds", [])
        font_size = element.get("TextSize")
        type_of_bounds = element.get("Path").split("/")
        type_of_bounds = type_of_bounds[len(type_of_bounds)-1]
        is_figure = "Figure" in type_of_bounds
        if text and bounds and not is_figure:
            draw_text(c,int(bounds[0]),int(bounds[2]),int(bounds[3]),text,font_size)
        if element and is_figure:
            try:
                figures = element.get("filePaths")[0].split("/")
                figure = figures[len(figures)-1]
                figure_path = os.path.join(work_path,file_name,"figures",figure)
                print(figure_path)
                draw_figure(c,figure_path,int(bounds[0]),int(bounds[1]),int(bounds[2]),int(bounds[3]))
            except:
                print("some error")
        previous_page = number_of_page

    c.save()