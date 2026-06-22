from flask import Flask, render_template, request, jsonify, session
import ollama
from pypdf import PdfReader
from docx import Document
import uuid

app = Flask(__name__)
app.secret_key = "my_secret_key"
SYSTEM_PROMPT = """
You are a friendly AI assistant.
Answer in English using simple language.
Keep answers concise and under 5 sentences unless more details are requested.
"""
CHUNK_SIZE = 1000
uploaded_documents = {}
uploaded_file_names = {}

@app.route("/")
def home():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    if "chat_history" not in session:
        session["chat_history"] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
    user_id = session["user_id"]
    question = request.json["question"]

    if user_id in uploaded_documents and len(uploaded_documents[user_id]) > 0:
        best_chunk = ""
        best_score = 0
        source_chunk = 0
        question_words = question.lower().split()

        for index, chunk in enumerate(uploaded_documents[user_id]):
            score = 0

            for word in question_words:
                if len(word) > 3 and word in chunk.lower():
                    score = score + 1

            if score > best_score:
                best_score = score
                best_chunk = chunk
                source_chunk = index + 1

        if best_chunk == "":
            best_chunk = uploaded_documents[user_id][0]
        
        print("\nQuestion:", question)
        print("Best chunk:", source_chunk)
        print("Score:", best_score)

        prompt = f"""Use the following document as the main source of information.

If the document contains the answer, use it.
If the document does not provide enough information, you may use your general knowledge to provide a helpful answer.

Context:
{best_chunk}
Question:
{question}
"""
    else:
        prompt = question
        
    session["chat_history"].append({
        "role": "user",
        "content": prompt
    })
    response = ollama.chat(
        model = "llama3.2",
        messages = session["chat_history"]
    )
    answer = response["message"]["content"]

    if user_id in uploaded_file_names:
        answer += f"\n\n **Based on:** {uploaded_file_names[user_id]}"

    session["chat_history"].append({
        "role": "assistant",
        "content": answer
    })
    return jsonify({"answer": answer})

@app.route("/clear", methods=["POST"])
def clear():
    user_id = session["user_id"]
    session["chat_history"] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if user_id in uploaded_documents:
        del uploaded_documents[user_id]

    return jsonify({"message": "Chat cleared"})

@app.route("/upload", methods=["POST"])
def upload_document():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_id = session["user_id"]
    file = request.files["document"]
    uploaded_file_names[user_id] = file.filename

    if file.filename.endswith(".txt"):
        text = file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif file.filename.endswith(".docx"):
        document = Document(file)
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
    else:
        return jsonify({"message": "Unsupported file type"})
    
    uploaded_documents[user_id] = []
    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i + CHUNK_SIZE]
        uploaded_documents[user_id].append(chunk)

    return jsonify({"message": "Document uploaded successfully"})

if __name__ == "__main__":
    app.run(debug=True)
