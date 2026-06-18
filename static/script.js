const questionInput = document.querySelector("#question");
const chatBox = document.querySelector("#chatBox");
const sendButton = document.querySelector("#sendButton");

sendButton.addEventListener("click", async function () {
    const question = questionInput.value;
    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerHTML = question;
    chatBox.appendChild(userMessage);

    questionInput.value = "";

    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    botMessage.innerHTML = "Bot is thinking...";
    chatBox.appendChild(botMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question
        })
    });
    const data = await response.json();
    botMessage.innerHTML = "<strong>AI Assistant</strong><br><br>" + data.answer;
    chatBox.scrollTop = chatBox.scrollHeight;
});

questionInput.addEventListener("keydown", function(event){
    if(event.key === "Enter")
    {
        sendButton.click();
    }
});