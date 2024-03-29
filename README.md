# EmailSummarization

The Email Quagmire: 
Average individuals spend 2+ hours daily sifting through emails. Missed emails burgeon into daunting threads, consuming even more precious time.
Major Concerns: 
1. Time it takes to catch-up
2. Missing mails

Hence, the aim is to do Abstractive Summarization for all the primary mails in the inbox

## Directory Structuring
<img width="334" alt="Screenshot 2024-03-26 at 11 53 29 PM" src="https://github.com/pallesaisamyukta/EmailSummarization/assets/20264867/1fe1b173-5480-49c8-9951-190ec1e834b6">


## Overview
This project consits of 2 main parts:
1. **PyTorch Modeling:** The dataset source is https://www.kaggle.com/datasets/marawanxmamdouh/email-thread-summary-dataset Then, unfroze the last 3 layers for Finetuning the BART Model. The saved model can be accessed here: https://drive.google.com/drive/folders/1eBbly0GhctrEJZHjuOGsd7PorejL2q43?usp=sharing

2. **Chrome Extension:** Through the extension, when a user enters their credentials then the system fetches emails from the user's inbox over the past week, extracts relevant content, generates a concise summary using BART, and sends it back to the user via email.

## Important Directories
1. ```models```: Store for all the trained models.
2. ```data/raw```: Store the Kaggle dataset as a csv
3. ```notebooks/```: Stores all the experimental files for TF-IDF & BART Finetuned jupyter notebooks.
4. ```backend/```: Store for all the scripts to run the training pipeline: training, evaluation & server. The main.py script is used to trigger the pipeline.
5. ```chrome-extension/```: Source code for managing & running the extension.


## Getting Started

### Steps to run the API server

```bash
cd EmailSummarization
pip install -r requirements.txt
uvicorn --backend.server:app
```

### Loading the Extension into Chrome

- Download and Unzip the Extension:
  First, clone this repository or download the zip file of the extension to your local machine. If downloaded as a zip, extract the contents to a folder of your choice.

- Open Chrome Extensions Page:
  Open the Google Chrome browser and navigate to the extensions page by entering chrome://extensions/ in the address bar. Alternatively, you can access this page by clicking on the three dots at the top-right corner of the browser, selecting 'More tools', and then selecting 'Extensions'.

- Enable Developer Mode:
  Toggle the 'Developer mode' switch on the top-right corner of the extensions page. This allows you to load unpacked extensions.

- Load the Unpacked Extension:
  Click on the 'Load unpacked' button which appears after enabling Developer Mode. Navigate to the folder where you extracted the extension files and select it. Ensure that you select the folder containing the manifest.json file.

- Verify Installation:
  After selecting the folder, the extension should now appear in your list of installed extensions. Ensure there are no errors and that the extension is enabled.

### Entrypoint for inference

POST request to `/summarize` like so:

```bash
curl --request POST \
  --url http://127.0.0.1:8000/summarize \
  --header 'Content-Type: application/json' \
  --data '{
	"email": "<ENTER_YOUR_EMAIL>",
	"password": “<ENTER_YOUR_PASSWORD>”
}'
```

### How to run training pipeline?
```
cd EmailSummarization
pip install -r requirements.txt
python main.py
```

Some of the libraries work only in Linux & MACOS.

## Contributors
* Abhishek Murthy (@rootsec1)
* Mrinoy Bannerjee (@mrinoybanerjee)
* Sai Samyukta Palle (@pallesaisamyukta)
