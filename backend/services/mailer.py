import imaplib
import email
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import torch
from transformers import BartForConditionalGeneration, BartTokenizer

# Retrieve necessary credentials and API keys from environment variables
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")


class EmailTLDR:
    """
    A class for summarizing emails received over a specified period and sending a summary via email.
    """

    def __init__(self, email_address, email_password):
        """
        Initializes the EmailTLDR object with email credentials and configures the Google Gemini API.

        Parameters:
        - email_address: The user's email address.
        - email_password: The password for the email account.
        - gemini_api_key: The API key for the Google Gemini API.
        """
        self.email_address = email_address
        self.email_password = email_password
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.sender_email = self.email_address
        self.recipient_email = self.email_address
        self.model_path = 'models/fine_tuned_bart_model.pt'
        self.connect_to_email()

    def connect_to_email(self):
        """
        Logs into the email server using the provided credentials.
        """
        self.mail.login(self.email_address, self.email_password)
        self.mail.select('"[Gmail]/All Mail"')

    def fetch_emails_since(self, days_ago=4):
        """
        Fetches emails from the last specified number of days.

        Parameters:
        - days_ago: The number of days in the past to retrieve emails from (default is 7).

        Returns:
        - A list of email IDs for the emails found within the specified period.
        """
        date_cutoff = (
            datetime.now() - timedelta(days=days_ago)
        ).strftime("%d-%b-%Y")
        status, messages = self.mail.search(None, f'(SINCE "{date_cutoff}")')
        if status == "OK":
            return messages[0].split()
        return []

    def extract_email_bodies(self, email_ids):
        """
        Extracts and decodes the bodies of emails given their IDs.

        Parameters:
        - email_ids: A list of email IDs.

        Returns:
        - A list of email bodies as strings.
        """
        bodies = ["" for _ in email_ids]
        for i, email_id in enumerate(email_ids):
            _, msg = self.mail.fetch(email_id, "(RFC822)")
            for response_part in msg:
                if isinstance(response_part, tuple):
                    email_message = email.message_from_bytes(response_part[1])
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True)
                                try:
                                    bodies[i] += body.decode('utf-8')
                                except UnicodeDecodeError:
                                    # Fallback encoding
                                    bodies[i] += body.decode('iso-8859-1')
                    else:
                        body = email_message.get_payload(decode=True)
                        try:
                            bodies[i] += body.decode('utf-8')
                        except UnicodeDecodeError:
                            bodies[i] += body.decode('iso-8859-1')
            bodies[i] = self.clean_body(bodies[i])
        return bodies

    @staticmethod
    def clean_body(body):
        """
        Cleans the body of an email from unnecessary characters.

        Parameters:
        - body: The raw email body as a string.

        Returns:
        - The cleaned email body as a string.
        """
        return body.replace("\r", "").replace("\n", "").replace("\u200c", "")

    def generate_summary(self, email_bodies, model_path):
        """
        Generates a summary of the provided email bodies using the finetuned BART model.

        Parameters:
        - email_bodies: A list of email bodies as strings.

        Returns:
        - A string containing the summary of the emails.
        """
        prompt = ("")
        # Limit to first 5 for brevity
        prompt += " : " + " ".join(email_bodies[:5])
        print(prompt)
        # Specify to load the model to CPU
        model = BartForConditionalGeneration.from_pretrained(
            'facebook/bart-base',
            state_dict=torch.load(model_path, map_location=torch.device('cpu'))
        )
        tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')
        inputs = tokenizer(
            [prompt],
            return_tensors="pt",
            max_length=1024,
            truncation=True
        )
        summary_ids = model.generate(
            inputs['input_ids'],
            num_beams=4,
            max_length=200,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def send_email(self, body):
        """
        Sends an email with the provided body to the user's email address.

        Parameters:
        - body: The body of the email to be sent.
        """
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        message['Subject'] = "Your Weekly Email-TLDR!"
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.sender_email, self.email_password)
        server.sendmail(
            self.sender_email,
            self.recipient_email,
            message.as_string()
        )
        server.quit()

    def summarize_and_send(self):
        """
        Fetches, summarizes, and sends an email summary of the user's inbox from the past week.
        """
        email_ids = self.fetch_emails_since()
        email_bodies = self.extract_email_bodies(email_ids)
        summary = self.generate_summary(email_bodies, self.model_path)
        self.send_email(summary)