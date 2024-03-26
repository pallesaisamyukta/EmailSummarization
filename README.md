# EmailSummarization

## Steps to run the API server

```bash
cd EmailSummarization
pip install -r requirements.txt
uvicorn --backend.server:app
```

## Loading the Extension into Chrome

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

## Entrypoint for inference

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
