from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import io
import re
from typing import Union

from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware


# Let's pick the desired backend
# os.environ['USE_TF'] = '1'
os.environ['USE_TORCH'] = '1'
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8100",
    "http://198.168.178.20:8100",
    "127.0.0.1",
    "*"
]

import matplotlib.pyplot as plt

from doctr.io import DocumentFile
from doctr.models import ocr_predictor, kie_predictor
predictor = ocr_predictor(det_arch="db_resnet50",reco_arch='crnn_mobilenet_v3_large', pretrained=True, detect_language=True, detect_orientation=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], expose_headers=["*"]
)

@app.get("/hw")
def read_root():
    return {"Hello": "World"}

def image_processing_stub(image_content: bytes):
    doc = DocumentFile.from_images(image_content)
    result = predictor(doc)
    return result

def search_ids(id_list, pattern1, pattern2):
    found_ids_letters_numbers = []
    found_ids_pure_numbers = []

    for string in id_list:
        # Search for the pattern with letters/numbers and "-"
        match1 = re.search(pattern1, string)
        if match1:
            found_ids_letters_numbers.append(match1.group(0))

        # Search for the pattern with pure numbers and more than 6 digits
        match2 = re.search(pattern2, string)
        if match2:
            found_ids_pure_numbers.append(match2.group(0))
    found_id_number=""
    found_id_letter=""
    if len(found_ids_letters_numbers)>0:
        found_id_letter = found_ids_letters_numbers[0]
    if len(found_ids_pure_numbers)>0:
        found_id_number = found_ids_pure_numbers[0]    
    return found_id_letter, found_id_number

@app.post("/process_image")
async def process_image(file:UploadFile = File(...)):
    print("here")
    print(file)
    # Read the image content
    image_content = await file.read()

    # Process the image (stubbed function)
    processed_result = image_processing_stub(image_content)

    # Search for IDs in the processed result
    pattern_letters_numbers = r"[A-Z0-9]+-[A-Z0-9]+"
    pattern_pure_numbers = r"\d{7,}"
    print("PROCESS")
    result_letters_numbers, result_pure_numbers = search_ids(processed_result.render().split('\n'), pattern_letters_numbers, pattern_pure_numbers)
    print(result_letters_numbers, result_pure_numbers)
    res = JSONResponse(content={"id": result_pure_numbers , "setID": result_letters_numbers,"language":processed_result.export()['pages'][0] ['language']['value']})
    print(res)

    # Return the results as JSON
    return res
