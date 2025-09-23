let firstInputDone = false;
let chatHistory = [];

const hide = id => document.getElementById(id)?.classList.add("hidden");
const show = id => document.getElementById(id)?.classList.remove("hidden");

function appendMessage(text, type="bot") {
    const box = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = `msg ${type}`;
const formatted = text
  .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")  // **bold**
  .replace(/\*(.*?)\*/g, "<em>$1</em>");             // *italic*

div.innerHTML = formatted.split(/\r?\n/).map(line => `<p>${line}</p>`).join('');

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function showTypingIndicator() {
    const messages = document.getElementById("messages");
    const indicator = document.createElement("div");
    indicator.id = "typing-indicator";
    indicator.innerHTML = "<span></span><span></span><span></span>";
    messages.appendChild(indicator);
    messages.scrollTop = messages.scrollHeight;
    return indicator;
}

function hideTypingIndicator(indicator) {
    if (indicator) indicator.remove();
}


// Save chat history to localStorage
function saveChatHistory(userMessage, botReply) {
    const chatHistory = JSON.parse(localStorage.getItem('healthBuddyChatHistory') || '[]');
    
    chatHistory.push({
        timestamp: new Date().toISOString(),
        message: userMessage,
        reply: botReply
    });
    
    // Keep only last 50 conversations
    if (chatHistory.length > 50) {
        chatHistory.splice(0, chatHistory.length - 50);
    }
    
    localStorage.setItem('healthBuddyChatHistory', JSON.stringify(chatHistory));
}

async function sendMessage(userMessage = null){
    const input = document.getElementById("userInput");
    const msg = userMessage || input.value.trim();
    if(!msg) return;

    if(!firstInputDone){
        hide("welcome-section");
        hide("quick-prompts");
        firstInputDone = true;
    }

    appendMessage(msg,"user"); 
    if (!userMessage) input.value = "";
    chatHistory.push({role:"user", content:msg});

    const indicator = showTypingIndicator();

    try{
        const r = await fetch("/chat",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({chat_history: chatHistory, message: msg})
        });
        const d = await r.json(); 
        
        hideTypingIndicator(indicator);
        
        appendMessage(d.reply || "", "bot");
        chatHistory.push({role:"assistant", content:d.reply || ""});
        
        // Save chat history to localStorage
        saveChatHistory(msg, d.reply || "");
    }catch{
        hideTypingIndicator(indicator);
        appendMessage("Error contacting server","bot");
    }
}

document.addEventListener("DOMContentLoaded",()=>{

    // Quick prompt click
    document.querySelectorAll(".prompt-btn").forEach(b=>{
        b.onclick = () => {
            document.getElementById("userInput").value = b.dataset.prompt;
            if(!firstInputDone){
                hide("welcome-section");
                hide("quick-prompts");
                firstInputDone = true;
            }
            sendMessage();
        };
    });

    // Premium ripple effect for all feature buttons
    document.querySelectorAll(".feature-btn").forEach(button => {
        button.addEventListener("click", (e) => {
            createRipple(e, button);
        });
    });

    // SOS popup logic
    const sosBtn = document.getElementById("sosBtn");
    const overlay = document.getElementById("sos-overlay");
    const closeBtn = document.getElementById("close-sos-btn");
    const sosAction = document.getElementById("sos-action-btn");

    // Premium SOS button click with ripple effect
    sosBtn.addEventListener("click", (e)=>{
        // Create ripple effect
        createRipple(e, sosBtn);
        
        // Show overlay with premium animation
        overlay.classList.remove("hidden");
        overlay.classList.add("active");
    });

    closeBtn.addEventListener("click", ()=>{
        overlay.classList.remove("active");
        setTimeout(()=> overlay.classList.add("hidden"), 300);
    });

    sosAction.addEventListener("click", ()=>{
        appendMessage("🚑 Calling ambulance...","bot");
        overlay.classList.remove("active");
        setTimeout(()=> overlay.classList.add("hidden"), 300);
    });

    // Navigation buttons functionality
    const userProfileBtn = document.getElementById("userProfileBtn");
    if (userProfileBtn) {
        userProfileBtn.addEventListener("click", (e)=>{
            console.log("User Profile button clicked!");
            createRipple(e, userProfileBtn);
            window.location.href = '/profile';
        });
    } else {
        console.error("User Profile button not found!");
    }

    document.getElementById("dashboardBtn").addEventListener("click", ()=>{
        sendMessage("📊 I want to see my health dashboard and track my progress");
    });

    document.getElementById("setGoalBtn").addEventListener("click", ()=>{
        sendMessage("🎯 I want to set my health goals and create a plan");
    });

    document.getElementById("checkSymptomsBtn").addEventListener("click", ()=>{
        sendMessage("🔍 I want to check my symptoms and get health advice");
    });

    document.getElementById("healthTipsBtn").addEventListener("click", ()=>{
        sendMessage("💡 I want to get daily health tips and wellness advice");
    });

    document.getElementById("emergencyFirstAidBtn").addEventListener("click", ()=>{
        sendMessage("🚨 I need emergency first aid guidance and immediate medical help");
    });



    // Enter send
    document.getElementById("userInput").addEventListener("keypress", e=>{
        if(e.key==="Enter") sendMessage();
    });

    // Minimize/Expand Sidebar functionality
    const minimizeBtn = document.getElementById("minimizeBtn");
    const sidebar = document.getElementById("sidebar-left");
    let isMinimized = false;

    minimizeBtn.addEventListener("click", (e) => {
        createRipple(e, minimizeBtn);
        
        if (isMinimized) {
            // Expand sidebar
            sidebar.classList.remove("minimized");
            sidebar.classList.add("expanded");
            minimizeBtn.textContent = "−";
            isMinimized = false;
        } else {
            // Minimize sidebar
            sidebar.classList.remove("expanded");
            sidebar.classList.add("minimized");
            minimizeBtn.textContent = "+";
            isMinimized = true;
        }
    });

    // Ripple effect function
    function createRipple(event, element) {
        const ripple = document.createElement("span");
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + "px";
        ripple.style.left = x + "px";
        ripple.style.top = y + "px";
        ripple.classList.add("ripple");
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

});
