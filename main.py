# Importing the necessary libraries
from backend.training import train_model


def main():
    '''
    calling train_model:
    1. Finetunes BART model
    2. Evaluates the model & saves it
    3. Uses the saved model for summaries
    '''
    train_model()


if __name__ == "__main__":
    main()
