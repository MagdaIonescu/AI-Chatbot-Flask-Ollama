from flask import Flask, render_template, request, jsonify
import ollama
from pypdf import PdfReader
from docx import Document

app = Flask(__name__)
chat_history = [
    {
        "role": "system",
        "content": "You are a friendly AI assistant. Answer in English using simple language. Keep answers concise and under 5 sentences unless more details are requested."
    }
]
document_text = ""

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/ask", methods=["POST"])
def ask():
    question = request.json["question"]

    if document_text != "":
        prompt = f"""Use the following document as the main source of information.

If the document contains the answer, use it.
If the document does not provide enough information, you may use your general knowledge to provide a helpful answer.

Context:
{document_text}
 Question:
{question}
"""
    else:
        prompt = question
        
    chat_history.append({
        "role": "user",
        "content": prompt
    })
    response = ollama.chat(
        model = "llama3.2",
        messages = chat_history
    )
    answer = response["message"]["content"]
    chat_history.append({
        "role": "assistant",
        "content": answer
    })
    return jsonify({"answer": answer})

@app.route("/clear", methods=["POST"])
def clear():
    global chat_history
    global document_text

    chat_history = [
        {
            "role": "system",
            "content": "You are a friendly AI assistant. Answer in English using simple language. Keep answers concise and under 5 sentences unless more details are requested."
        }
    ]
    document_tex = ""
    return jsonify({"message": "Chat cleared"})

@app.route("/upload", methods=["POST"])
def upload_document():
    global document_text
    
    file = request.files["document"]
    if file.filename.endswith(".txt"):
        document_text = file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        document_text = text
    elif file.filename.endswith(".docx"):
        document = Document(file)
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        document_text = text
    else:
        return jsonify({"message": "Unsupported file type"})
    return jsonify({"message": "Document uploaded successfully"})

if __name__ == "__main__":
    app.run(debug=True)
