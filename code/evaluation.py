from rouge import Rouge

def rouge_metric(original_emails, generated_emails):
    rouge_scores = []
    num_samples = len(original_emails)
    for i in range(num_samples):
        generated_summary = generated_emails[i]
        original_text = original_emails[i]

        # Initialize the Rouge object
        rouge = Rouge()
        
        # Compute ROUGE scores
        score = rouge.get_scores(generated_summary, original_text)
        rouge_scores.append(score)

    # Calculate average ROUGE scores
    avg_scores = {'rouge-1': {'r': 0, 'p': 0, 'f': 0},
                  'rouge-2': {'r': 0, 'p': 0, 'f': 0},
                  'rouge-l': {'r': 0, 'p': 0, 'f': 0}}


    for score in rouge_scores:
        for metric in score[0]:
            avg_scores[metric]['r'] += score[0][metric]['r']
            avg_scores[metric]['p'] += score[0][metric]['p']
            avg_scores[metric]['f'] += score[0][metric]['f']

    for metric in avg_scores:
        avg_scores[metric]['r'] /= num_samples
        avg_scores[metric]['p'] /= num_samples
        avg_scores[metric]['f'] /= num_samples

    return avg_scores