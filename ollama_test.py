import ollama

ocr_response = [
    {"text": "BuII", "confidence": 0.997, "bounding_box": "Array(4)"},
    {"text": "CELSIUS", "confidence": 0.972, "bounding_box": "Array(4)"},
    {"text": "DRIN", "confidence": 0.945, "bounding_box": "Array(4)"},
    {"text": "SparkIing", "confidence": 0.450, "bounding_box": "Array(4)"}
]

cleaned_text = []
for item in ocr_response:
    text = item["text"]
    cleaned_text.append(text)

# Format the cleaned text for input to Llama
ocr_text_for_llama = " ".join(cleaned_text)

response = ollama.chat(
    model='llama3.2',
    messages=[{
        'role': 'user',
        'content': f"Here are the items extracted from a receipt: {ocr_text_for_llama}. Can you identify the objects or products each under 5 words"
    }]
)

print(response)