import json
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from torch.utils.data import Dataset
# NEW: Import drive to access persistent storage
from google.colab import drive

class RiskSummaryDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.data = data
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        input_text = f"Input: {item['input']}\nOutput:"
        output_text = item['output']

        input_encoding = self.tokenizer(input_text, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt')
        output_encoding = self.tokenizer(output_text, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt')

        input_ids = torch.cat([input_encoding['input_ids'].squeeze(), output_encoding['input_ids'].squeeze()], dim=0)
        attention_mask = torch.cat([input_encoding['attention_mask'].squeeze(), output_encoding['attention_mask'].squeeze()], dim=0)
        labels = input_ids.clone()

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

def main():
    # NEW: Mount Google Drive
    # This will trigger a popup asking for permission to access your Drive files
    drive.mount('/content/drive')

    # Load data (Make sure you upload 'training_data.json' to Colab files on the left!)
    # Updated path to load from Google Drive
    with open('/content/drive/MyDrive/training_data.json', 'r') as f:
        data = json.load(f)

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    dataset = RiskSummaryDataset(data, tokenizer)

    # NEW: Define a path inside your Google Drive
    # This ensures checkpoints and the final model are saved permanently
    save_path = '/content/drive/MyDrive/risk_summary_model'

    training_args = TrainingArguments(
        output_dir=f'{save_path}/results', # Updated path
        num_train_epochs=50,
        per_device_train_batch_size=2,
        save_steps=500,
        save_total_limit=2,
        logging_dir=f'{save_path}/logs',   # Updated path
        logging_steps=10,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=100,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    trainer.train()

    # NEW: Save final model to Drive
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    print(f"Model successfully saved to {save_path}")

if __name__ == "__main__":
    main()