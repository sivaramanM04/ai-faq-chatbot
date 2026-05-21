const sendBtn = document.getElementById("sendBtn");

const userInput = document.getElementById("userInput");

const chatBox = document.getElementById("chatBox");

const domainSelect = document.getElementById("domainSelect");

const historySection = document.getElementById(
    "historySection"
);

const newChatBtn = document.querySelector(
    ".new-chat-btn"
);

// ====================================
// DOMAIN SUGGESTIONS
// ====================================

const suggestionData = {

    "College FAQs":[

        "What is the admission process?",

        "What are the hostel fees?",

        "When do exams start?",

        "What courses are available?"

    ],

    "HR Support":[

        "How many leave days are allowed?",

        "How to apply for leave?",

        "What is company policy?",

        "How to access payroll?"

    ],

    "Customer Support":[

        "How to contact support?",

        "Where is my order?",

        "How to request refund?",

        "How to track shipment?"

    ],

    "Product Assistance":[

        "How to reset device?",

        "How to install software?",

        "Why is the product not working?",

        "How to update firmware?"

    ]

};

// ====================================
// LOAD SUGGESTIONS
// ====================================

function loadSuggestions(domain){

    const container =
    document.getElementById(
        "suggestionContainer"
    );

    if(!container){

        return;

    }

    // CLEAR OLD

    container.innerHTML = "";

    // GET DOMAIN DATA

    const suggestions =
    suggestionData[domain];

    // CREATE NEW SUGGESTIONS

    suggestions.forEach((text) => {

        const div =
        document.createElement("div");

        div.classList.add(
            "chat-suggestion"
        );

        div.innerText = text;

        // CLICK EVENT

        div.addEventListener(
            "click",
            () => {

                userInput.value = text;

                sendMessage();

            }
        );

        container.appendChild(div);

    });

}

// ====================================
// ADD MESSAGE
// ====================================

function addMessage(message, className){

    const div =
    document.createElement("div");

    div.classList.add("message");

    div.classList.add(className);

    div.innerHTML = message;

    chatBox.appendChild(div);

    chatBox.scrollTop =
    chatBox.scrollHeight;
}

// ====================================
// UPDATE HISTORY
// ====================================

function addHistory(message){

    const emptyHistory =
    document.querySelector(
        ".empty-history"
    );

    if(emptyHistory){

        emptyHistory.remove();

    }

    const historyItem =
    document.createElement("div");

    historyItem.classList.add(
        "history-item"
    );

    historyItem.innerHTML = `

        <i class="fa-regular fa-message"></i>

        <span>

            ${message.substring(0,30)}

        </span>

    `;

    historySection.prepend(
        historyItem
    );
}

// ====================================
// SEND BUTTON
// ====================================

sendBtn.addEventListener(
    "click",
    sendMessage
);

// ====================================
// ENTER KEY
// ====================================

userInput.addEventListener(
    "keypress",
    function(e){

        if(e.key === "Enter"){

            sendMessage();

        }

    }
);

// ====================================
// DOMAIN CHANGE
// ====================================

domainSelect.addEventListener(
    "change",
    () => {

        loadSuggestions(
            domainSelect.value
        );

    }
);

// ====================================
// NEW CHAT
// ====================================

newChatBtn.addEventListener(
    "click",
    () => {

        // RESET CHAT SCREEN

        chatBox.innerHTML = `

            <div class="welcome-area">

                <div class="message bot-message">

                    Hello 👋 How can I help you today?

                </div>

                <div class="chat-suggestions"
                id="suggestionContainer">

                </div>

            </div>

        `;

        // RELOAD SUGGESTIONS

        loadSuggestions(
            domainSelect.value
        );

    }
);

// ====================================
// SEND MESSAGE
// ====================================

async function sendMessage(){

    const message =
    userInput.value.trim();

    const domain =
    domainSelect.value;

    if(message === "") return;

    // REMOVE WELCOME AREA

    const welcomeArea =
    document.querySelector(
        ".welcome-area"
    );

    if(welcomeArea){

        welcomeArea.remove();

    }

    // USER MESSAGE

    addMessage(
        message,
        "user-message"
    );

    // UPDATE HISTORY

    addHistory(message);

    // CLEAR INPUT

    userInput.value = "";

    // LOADING

    const loadingDiv =
    document.createElement("div");

    loadingDiv.classList.add(
        "message",
        "bot-message"
    );

    loadingDiv.innerHTML =
    "Typing...";

    chatBox.appendChild(
        loadingDiv
    );

    chatBox.scrollTop =
    chatBox.scrollHeight;

    try{

        const response =
        await fetch(
            '/chat',
            {

                method:'POST',

                headers:{
                    'Content-Type':
                    'application/json'
                },

                body:JSON.stringify({

                    message:message,

                    domain:domain

                })

            }
        );

        const data =
        await response.json();

        loadingDiv.remove();

        addMessage(
            data.response,
            "bot-message"
        );

    }

    catch(error){

        loadingDiv.remove();

        addMessage(
            "Server Error",
            "bot-message"
        );

    }

}

// ====================================
// INITIAL LOAD
// ====================================

loadSuggestions(
    domainSelect.value
);