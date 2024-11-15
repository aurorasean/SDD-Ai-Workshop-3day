const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatOutput = document.querySelector("#chat-output");
const welcome = document.querySelector("#welcome");
const dots = document.querySelector("#dots");

const getChatResponse = async (text) => {
    var url = `/assistant?input=${text}`;
    var response = await fetch(url);
    var text = await response.text();
    return text;
}

const handleOutgoingChat = async () => {
    // Get user input and make sure it isn't empty
    var text = chatInput.value.trim();
    if(!text) return;

    // Clear the input field and reset its height
    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    // Hide the output and show the dancing dots
    welcome.style.display = "none";
    chatOutput.style.display = "none";
    dots.style.display = "block";

    try {
        // Get a response from the server
        var text = await getChatResponse(text);

        if (text.startsWith("data:image/png;")) {
            // Show an image
            chatOutput.innerHTML = `<img src="${text}" class="zoom" alt="chart" >`;
        }
        else {
            // Show text
            chatOutput.innerHTML = `<p class="zoom">${text.replaceAll("\n", "<br>")}</p>`;
        }
    }
    catch(error) {
        // Show an error message
        chatOutput.innerHTML = `I'm sorry, but something went wrong ($(error.message))`;
    }
    finally {
        // Show the output and hide the dancing dots
        chatOutput.style.display = "block";
        dots.style.display = "none";
    }
}

chatInput.addEventListener("input", () => {   
    // Adjust the height of the input field dynamically based on its content
    chatInput.style.height =  `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", async (e) => {
    // If the Enter key is pressed without Shift and the window width is larger 
    // than 800 pixels, handle the outgoing chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

sendButton.addEventListener("click", handleOutgoingChat);
const initialInputHeight = chatInput.scrollHeight;