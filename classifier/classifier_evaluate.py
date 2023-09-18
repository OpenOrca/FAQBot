import pandas as pd
from vllm import LLM, SamplingParams
from pprint import pprint

# Load the parquet dataset
df = pd.read_parquet('qa_classifier.parquet')

# Prepare the LLM model
sampling_params = SamplingParams(temperature=0, max_tokens=8, use_beam_search=True, best_of=3)
llm = LLM(model="eugenepentland/axolotl_question_classifier", tokenizer='hf-internal-testing/llama-tokenizer')

def generate_prompt(message):
    message = message.replace("?","")
    return f"""
User:
1. Standalone questions are typically short.
2. They frequently begin with a question word (like "Is", "Can", "Does", "How").
3. They pertain to the technical aspects of a machine learning software/tool named "Axolotl", "QLora", "Deepspeed", "FSDP", "Llama".
4. They seek clarity on the capabilities, methods, or functionalities without extended context.
5. If you aren't sure what the answer is, say its not a question.

Please evaluate the following message using the following rules

"{message}"

Is this a standalone question based on the predefined patterns?"""


# Convert each instruction to a prompt using the new template
all_prompts = [generate_prompt(instruction) for instruction in df['instruction'].tolist()]

# Generate responses for all prompts at once
outputs = llm.generate(all_prompts, sampling_params)

# Check results
pass_correct = 0
fail_correct = 0
total_pass = sum(df['output'] == 'pass')
total_fail = sum(df['output'] == 'fail')

for i, output in enumerate(outputs):
    expected_output = df.iloc[i]['output']
    generated_text = output.outputs[0].text.strip().lower()  # Adding normalization here
    correct = False
    if expected_output == 'fail' and 'not' in generated_text:
        fail_correct += 1
        correct = True
    elif expected_output == 'pass' and not 'not' in generated_text:
        pass_correct += 1
        correct = True

    result = {
        "message": df.iloc[i]['instruction'],
        "correct_answer": expected_output,
        "generated_answer": generated_text
    }
    if not correct:
        pprint(result)

# Calculate the accuracy
pass_accuracy = pass_correct / total_pass * 100
fail_accuracy = fail_correct / total_fail * 100
overall_accuracy = (pass_accuracy + fail_accuracy) / 2
print(f"Accuracy for PASS: {pass_accuracy:.2f}%")
print(f"Accuracy for FAIL: {fail_accuracy:.2f}%")
print(f"Overall Accuracy: {overall_accuracy:.2f}%")