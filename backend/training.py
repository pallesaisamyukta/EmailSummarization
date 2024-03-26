import torch
import pandas as pd
from transformers import BartTokenizer, BartForConditionalGeneration, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import Dataset, DataLoader
from tqdm.auto import tqdm
from sklearn.model_selection import train_test_split


# Custom dataset class
class EmailDataset(Dataset):
    """
    PyTorch Dataset class for email summarization.

    Parameters:
    - tokenizer: The tokenizer object.
    - data: The DataFrame containing the email data.
    - max_length: The maximum length of the input sequence.
    - summary_length: The length of the summary sequence.

    Returns:
    - Dictionary containing the input_ids, attention_mask, and labels.
    """

    def __init__(self, tokenizer, data, max_length=512, summary_length=128):
        self.tokenizer = tokenizer
        self.data = data
        self.max_length = max_length
        self.summary_length = summary_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data.iloc[idx]
        thread = item['body']  # Assuming 'body' contains the email threads
        summary = item['summary']

        model_input = self.tokenizer(thread, max_length=self.max_length,
                                     truncation=True, padding='max_length', return_tensors="pt")
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(summary, max_length=self.summary_length,
                                    truncation=True, padding='max_length', return_tensors="pt")

        model_input["labels"] = labels["input_ids"].squeeze()

        return {key: val.squeeze() for key, val in model_input.items()}


def train_model():
    """
    Function to train the BART model for email summarization.
    """
    # Load dataset from CSV
    df = pd.read_csv("data/raw/merged_email_data.csv")

    # Initialize tokenizer
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')

    # Split dataset into train and validation sets
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

    # Prepare train and validation datasets
    train_dataset = EmailDataset(tokenizer, train_df)
    val_dataset = EmailDataset(tokenizer, val_df)

    # Initialize DataLoader for train and validation sets
    # Increased batch size for faster training
    train_dataloader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    # Increased batch size for faster evaluation
    val_dataloader = DataLoader(val_dataset, batch_size=8)

    # Initialize BART model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bart_model = BartForConditionalGeneration.from_pretrained(
        'facebook/bart-base')
    bart_model.to(device)

    # Prepare optimizer and scheduler
    optimizer = AdamW(bart_model.parameters(), lr=5e-5)
    epochs = 5
    total_steps = len(train_dataloader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    # Fine-tuning
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        bart_model.train()
        for batch in tqdm(train_dataloader, desc=f"Epoch {epoch + 1}/{epochs}"):
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = bart_model(
                input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            scheduler.step()

    # Save the fine-tuned model
    torch.save(bart_model.state_dict(), "models/email_summarizer_bart.pth")
