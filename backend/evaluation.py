import torch
from tqdm.auto import tqdm
from datasets import load_metric
from bert_score import score as bert_score
from transformers import logging as hf_logging
from random import sample

# Suppress verbose output from Transformers
hf_logging.set_verbosity_error()

class ModelEvaluator:
    """
    A class for evaluating text summarization models using ROUGE and BERTScore metrics.

    Attributes:
        model (PreTrainedModel): The model to evaluate.
        tokenizer (PreTrainedTokenizer): The tokenizer used with the model.
        device (torch.device): The device to run the evaluation on.
    """
    def __init__(self, model, tokenizer, device):
        """
        Initializes the ModelEvaluator with a model, tokenizer, and device.
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.eval()  # Set the model to evaluation mode.

    def evaluate(self, dataloader):
        """
        Evaluates the model on a given dataset using ROUGE and BERTScore metrics.

        Args:
            model (PreTrainedModel): The model to evaluate.
            dataloader (DataLoader): DataLoader providing the dataset for evaluation.
            device (torch.device): The device to run the evaluation on.

        Returns:
            A tuple of dictionaries containing ROUGE scores and BERT scores.
        """
        
        rouge = load_metric("rouge")
        bert_scores = {"precision": [], "recall": [], "f1": []}  # To store BERTScore
        self.model.eval() # Set the model to evaluation mode.
        
        progress_bar = tqdm(dataloader, desc="Evaluating", leave=False)
        
        all_preds = []
        all_references = []

        for batch in progress_bar:
            # Move batch to the specified device.
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)

            with torch.no_grad():
                # Generate summaries.
                generated_ids = self.model.generate(input_ids, attention_mask=attention_mask, max_length=128, num_beams=4, early_stopping=True)
                preds = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in generated_ids]
                references = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in labels]
                
                all_preds.extend(preds)
                all_references.extend(references)

                # Add predictions and references to ROUGE for batch evaluation.
                rouge.add_batch(predictions=preds, references=references)

        # BERTScore evaluation on a random subset to manage computation time.
        sample_size = 100  # Number of samples to evaluate BERTScore on.
        if len(all_preds) > sample_size:
            sampled_indices = sample(range(len(all_preds)), sample_size)
            sampled_preds = [all_preds[i] for i in sampled_indices]
            sampled_references = [all_references[i] for i in sampled_indices]
        else:
            sampled_preds, sampled_references = all_preds, all_references

        # Calculate BERTScore for the sampled predictions and references.
        P, R, F1 = bert_score(sampled_preds, sampled_references, lang="en", verbose=False)
        bert_scores["precision"].extend(P.tolist())
        bert_scores["recall"].extend(R.tolist())
        bert_scores["f1"].extend(F1.tolist())

        # Calculate average BERT scores.
        rouge_result = rouge.compute()
        rouge_scores = {key: value.mid.fmeasure * 100 for key, value in rouge_result.items()}

        avg_bert_scores = {
            "precision": sum(bert_scores["precision"]) / len(bert_scores["precision"]),
            "recall": sum(bert_scores["recall"]) / len(bert_scores["recall"]),
            "f1": sum(bert_scores["f1"]) / len(bert_scores["f1"]),
        }

        return rouge_scores, avg_bert_scores
