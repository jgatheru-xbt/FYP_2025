import torch
import os
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class RiskSummaryGenerator:
    def __init__(self, model_path=None):
        if model_path is None:
            # Default to 'risk_summary_model' directory at the project root.
            # This script is in Backend/, so we go up two levels to the project root.
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(project_root, 'risk_summary_model')
        else:
            model_path = os.path.abspath(model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model directory {model_path} does not exist. Please train the model first.")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        self.model = GPT2LMHeadModel.from_pretrained(model_path)
        self.model.eval()

    def generate_summary(self, input_data, max_length=300):
        """
        Generate a risk summary based on input simulation data.

        Args:
            input_data (str): Description of simulation metrics, e.g., "Encryption speed: 41.6 files/sec, Files encrypted: 500, Time: 12 seconds, Algorithm: AES-256"
            max_length (int): Maximum length of generated text

        Returns:
            str: Generated risk summary report
        """
        prompt = f"Input: {input_data}\nOutput:"

        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        attention_mask = torch.ones_like(input_ids)

        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        print(f"Full generated text: '{generated_text}'")
        # Extract only the output part
        if "Output:" in generated_text:
            summary = generated_text.split("Output:", 1)[1].strip()
        else:
            summary = generated_text
        print(f"Extracted summary: '{summary}'")

        # Fallback: if summary is empty or too short, generate template-based report
        if not summary or len(summary) < 50:
            print("Using fallback template report")
            summary = self._generate_template_report(input_data)

        return summary

    def _generate_template_report(self, input_data):
        """Generate a simple template-based report if AI generation fails."""
        # Parse input
        speed = 0
        files = 0
        time_taken = 0
        algorithm = "Unknown"
        
        try:
            parts = input_data.split(", ")
            for part in parts:
                if "Encryption speed:" in part:
                    speed = float(part.split()[2])
                elif "Files encrypted:" in part:
                    files = int(part.split()[2])
                elif "Time:" in part:
                    time_taken = float(part.split()[1])
                elif "Algorithm:" in part:
                    algorithm = part.split()[1]
        except:
            pass
        
        # Determine severity
        if speed > 50:
            severity = "CRITICAL"
            threat = f"Extremely high encryption speed ({speed} files/sec) indicates sophisticated attack."
            impact = "Immediate total data loss possible."
            mitigation = "1. Isolate system immediately. 2. Activate emergency response. 3. Prepare forensics."
        elif speed > 20:
            severity = "HIGH"
            threat = f"High encryption speed ({speed} files/sec) suggests ransomware activity."
            impact = "Significant data at risk within minutes."
            mitigation = "1. Stop the process. 2. Check backups. 3. Scan for malware."
        elif speed > 5:
            severity = "MEDIUM"
            threat = f"Moderate encryption activity ({speed} files/sec) detected."
            impact = "Potential data loss if not addressed."
            mitigation = "1. Monitor closely. 2. Investigate source. 3. Implement restrictions."
        else:
            severity = "LOW"
            threat = f"Slow encryption rate ({speed} files/sec), likely benign."
            impact = "Minimal immediate threat."
            mitigation = "1. Log activity. 2. Verify authorization. 3. Continue monitoring."
        
        report = f"[AI SECURITY REPORT: {severity}]\n\n"
        report += f"Threat Analysis: {threat}\n\n"
        report += f"Business Impact: {impact}\n\n"
        report += f"Mitigation: {mitigation}"
        
        return report

# Example usage
if __name__ == "__main__":
    generator = RiskSummaryGenerator()
    input_data = "Encryption speed: 41.6 files/sec, Files encrypted: 500, Time: 12 seconds, Algorithm: AES-256"
    summary = generator.generate_summary(input_data)
    print(summary)