from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)
chat_history = [
    {
        "role": "system",
        "content": "You are a friendly AI assistant. Answer in English using simple language. Keep answers concise and under 5 sentences unless more details are requested."
    }
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods = ["POST"])
def ask():
    question = request.json["question"]
    chat_history.append({
        "role": "user",
        "content": question
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

if __name__ == "__main__":
    app.run(debug=True)
