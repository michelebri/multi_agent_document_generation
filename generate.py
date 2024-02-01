import json    
import numpy as np
from PIL import Image, ImageTk
import os 
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog
from structure_extractor import StructureExtractor
from pdf import *
import fitz
from functools import partial


class Generation():

    def __init__(self):

        self.log_execution = ""

        self.structureExtractor = StructureExtractor()
        self.client = OpenAI()
        self.elements = []
        self.box_to_elaborate = 0

        #Initialization first GUI in order to choose a pdf file and obtain a json
        self.principal_window = tk.Tk()
        self.principal_window.geometry(f'{400}x{100}')
        self.principal_window.title("Create file with LLM")

        # I skip the choose in debug TODO: Remove the comment for the following two lines and remove the call a self.open_prompt_window()
        button_choose_pdf = tk.Button(self.principal_window,text="choose pdf template",command=self.open_prompt_window)
        button_choose_pdf.grid(padx=130, pady=40, sticky="nsew")   

        #self.open_prompt_window()
        self.principal_window.mainloop()



       

    def open_prompt_window(self):
        #chosee here the pdf not in the create_document function TODO : CHANGE
        #self.pdf_path = filedialog.askopenfilename(initialdir="dataset", title="Select gc game file", filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))
        self.pdf_path = "dataset/cover-letter-template-33250.pdf"
        #TODO: Also for the json_path, use the structure extacture to obtain the path
        #self.json_path = self.structureExtractor.extract_structure(self.pdf_path)
        self.json_path = "dataset/json/cover-letter-template-33250.json"
        #self.pdf_path = "dataset/Overleaf/Letter/hust-recommendation-letter-template.pdf"
        
        #Create conversiontal GUI to inteact with LLMs
        self.principal_window.destroy()  
        print("destroyed")
        self.principal_window = tk.Tk()
        self.principal_window.geometry(f'{1200}x{600}')
        instructions = tk.Label(self.principal_window, text="Insert the prompt with the data \n and the information to insert in the document\n")
        instructions.place(x = 100, y = 10)
        blank_image = Image.new("L", (400, 400), (120))
        self.show_rect_pdf = ImageTk.PhotoImage(blank_image)

        # display the image, now blank after the rect of pdf
        self.image_of_pdf = tk.Label(self.principal_window, image=self.show_rect_pdf)
        self.image_of_pdf.place(x= 650,y=100)
        
        self.prompt_preview = tk.Text(self.principal_window)
        self.prompt_preview.config(state='disabled')
        self.prompt_preview.place(x=50, y=120, height=200, width=500)
        self.text_prompt = tk.Text(self.principal_window)
        self.text_prompt.place(x=50, y=340, height=200, width=500)
        self.button_create_document = tk.Button(self.principal_window,text="Start the creation process",command=self.create_document)
        self.button_create_document.place(x=180,y=550)
        self.button_skip = tk.Button(self.principal_window,text="Skip section",state="disabled")
        self.button_skip.place(x=900,y=550)
        self.principal_window.mainloop()


    def create_document(self):
        """
        Take the structure and pass to an LLM the text and the semantic value.
        At the end the output will be a pdf that has the structure of template with LLM's text

        """
        #Populate the prompt preview with the first prompt
        self.final_prompt = self.text_prompt.get("1.0",'end-1c')
        self.log_execution += "The prompt is : \n" + self.final_prompt
        self.update_preview_prompt(self.final_prompt)
        self.text_prompt.delete("1.0", tk.END)

        #Populate the elements vector with all the elements of the pdf file
        with open(os.path.join(os.path.dirname(self.json_path),os.path.basename(self.json_path)), "r") as json_file:
            json_data = json.load(json_file)
        #Populate the elements vector with all elements of json and open the document for extract the BBox
        self.elements = json_data
        self.pdf_document = fitz.open(self.pdf_path) 
        self.pdf_to_image()

   
    def pdf_to_image(self):  
        if self.box_to_elaborate < len(self.elements["elements"]):
            
            #Take from the list the first element and increase the index for the future next iteration
            element = self.elements["elements"][self.box_to_elaborate]
            self.box_to_elaborate +=1

            #Obtain the necessary info from the json structure
            text = (element.get("Text"))
            bounds = element.get("Bounds")
            number_of_page = element.get("Page")

            matrix = fitz.Matrix(2, 2)  
            matrix.prescale(1 / 2.0, 1 / 2.0)
            height = (bounds[3] - bounds[1])
            width =bounds[2] - bounds[0] 

            page = self.pdf_document[number_of_page]
            dict_ = page.get_text('dict')
            height_page = dict_["height"]

            bounds = (bounds[0], height_page-bounds[1] - height,bounds[0]+width,(height_page-bounds[1]) + height/4)

            pix = page.get_pixmap(matrix=matrix, clip=bounds)
            width, height = pix.width, pix.height
            box_field = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.show_rect_pdf = ImageTk.PhotoImage(box_field)

            # Update the image displayed in the label
            self.image_of_pdf.config(image=self.show_rect_pdf)
            if not text:
                self.pdf_to_image()
            else:
                self.button_skip.configure(state="normal",command=self.pdf_to_image)
                process_element_wrapper = partial(self.process_element, [element,text])
                self.button_create_document.configure(text="Modify section",command=process_element_wrapper)
                self.button_create_document.place(x=700,y=550)
        else:
            self.generate_pdf()


    def process_element(self,arguments):

        """
            Generate with response the semantic value of the text that might be replaced!
            It's important choose right prompt
            With the input as response (an istruction), the ouput with field_filling_response will be the new text generated by LLM
        """
        element = arguments[0]
        text = arguments[1]

        self.log_execution += "\nThe actually prompt is \n" + self.final_prompt

        self.log_execution += "\nThe text in the document is \n" + text
        #Obtain the prompt inserted by the user

        
        field_identification_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens= 50,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are an assistant helping to understand the structure content of a template document. \
                            You are given a piece of text from a document and respond with the content that might be written in the document.\
                Give just the action to do. For example if you read Location the output will be Add the location."},
                {"role": "user", "content": text},
            ]
        )
        
        self.identified_fields = (field_identification_response.choices[0].message.content)
        self.log_execution += "\nThe field agent answer is \n" +(self.identified_fields)
        #I have reduced the token of this agent

        missing_information_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens= 50,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are an assistant that have the purpouse to search which information are missing.\n\
                        Your output must be like this : The missing information to satisy the request are INFORMATION_MISSING.\
                        If you have the information write the token [ALL INFO].\n\
                        Strictly response with just the information that are missing."
                },
                {"role": "user", "content": "I have this information : \n " + self.final_prompt + " \n\
                             I want satisfy this instruction \n" + self.identified_fields +\
                                " What are the missing information?"},
            ]
        )

        self.missing_information_prompt = (missing_information_response.choices[0].message.content)
        
        self.log_execution += "\nThe missing agent answer is \n" + (self.missing_information_prompt)
        #Show to the user the missing instruction
        self.update_preview_prompt("Istruction prompt : " + "\n" + self.identified_fields + "\n to satisfy insert : \n" + self.missing_information_prompt)

        update_information_with_parameters = partial(self.update_information, [element,text])
        # Restyle the button of GUI in order to have a new function. Now the button update the prompt's information 
        self.button_create_document.configure(text="Add the missing information", command=update_information_with_parameters)

        self.button_create_document.place(x=180,y=550)



    def update_information(self,arguments):

        if "[ALL INFO]" in self.missing_information_prompt:
            add_instruction = ".\nFor this section respect majorly this prompt : "+ missing_istruction + " and fill the document with this instruction " 
        else:
            add_instruction = ""
            missing_istruction = self.text_prompt.get("1.0",'end-1c')
            self.final_prompt = self.final_prompt +  ".\n" + missing_istruction
        element = arguments[0]
        text = arguments[1]
        max_tok = int(len(text)/4)
        if max_tok> 100:
            max_tok = int(max_tok*2)
        field_filling_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens= max_tok,
            temperature = 0,
            messages=[
                {"role": "system", "content": "Respect strongly the request prompt and respond with only the text that follow the request \
                The information that you have are : " + self.final_prompt +"If it is a body or purpouse or a content (principal part) of document never write the conclusion.\n \
                     For example if you read please enter the location you write just the location. \
                     Avoid any type of salutation or conclusion , you can write this content only if it's written in the prompt."},
                {"role": "user", "content": add_instruction + self.identified_fields  },
            ]
        )
        response_filling = (field_filling_response.choices[0].message.content)
        print(response_filling)
        if response_filling != "[NONE]":
            element["Text"] = response_filling
        self.log_execution += "\nThe filling agent answer is \n" +(response_filling)
        self.pdf_to_image()
            

    def update_preview_prompt(self,new_prompt):
        self.prompt_preview.config(state='normal')
        self.prompt_preview.delete("1.0", tk.END)
        self.prompt_preview.insert(tk.END, new_prompt)
        self.prompt_preview.config(state='disabled')

    def generate_pdf(self):
        text_file = open("log.txt", "w")
        text_file.write(self.log_execution)
        text_file.close()
        with open(os.path.join(os.path.dirname(self.json_path),"updated_json_file.json"), "w") as updated_json_file:
            json.dump(self.elements, updated_json_file, indent=2)

        self.principal_window.destroy()
        json_path_updated = os.path.join(os.path.dirname(self.json_path),"updated_json_file.json")
        create_pdf_from_json(json_path_updated, os.path.basename(self.json_path).replace(".json",""),json_path_updated.replace(".json",".pdf"))
        os.system('xdg-open ' +  json_path_updated.replace(".json",".pdf"))

Generation()
        
        
