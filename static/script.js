const questionInput = document.querySelector("#question");
const chatBox = document.querySelector("#chatBox");
const sendButton = document.querySelector("#sendButton");
const clearButton = document.querySelector("#clearButton");
const documentInput = document.querySelector("#documentInput");
const fileName = document.querySelector("#fileName");
const uploadButton = document.querySelector("#uploadButton");
const themeButton = document.querySelector("#themeButton")

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

clearButton.addEventListener("click", async function () {
    await fetch("/clear", {
        method:"POST"
    });
    chatBox.innerHTML = `<div class="bot-message"><strong>AI Assistant</strong><br><br>Hello! How can I help you today?</div>`;
    documentInput.value = "";
    fileName.innerText = "No file selected";
});

documentInput.addEventListener("change", function(){
    if(this.files.length > 0)
    {
        fileName.innerText = this.files[0].name;
    }
    else{
        fileName.innerText = "No file selected";
    }
});

uploadButton.addEventListener("click", async function () {
    const file = documentInput.files[0];
    if(!file)
    {
        alert("Please select a document!");
        return;
    }
    const formData = new FormData();
    formData.append("document", file);
    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });
    const data = await response.json();
    alert(data.message);
});

themeButton.addEventListener("click", function(){
    document.body.classList.toggle("dark-mode");
    if(document.body.classList.contains("dark-mode"))
    {
        themeButton.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }
    else
    {
        themeButton.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }
});