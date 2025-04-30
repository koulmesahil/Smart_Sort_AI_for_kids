import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="🎤 Voice Input", layout="centered")

st.title("🎤 Voice Command Demo (Web Speech API)")

st.markdown("Click 'Start Listening', say something, then click 'Stop Listening'.")
st.markdown("The recognized speech will appear below:")

# Web Speech API HTML block
html_code = """
<div style="text-align: center;">
  <button onclick="startListening()" style="font-size:18px;padding:10px 20px;margin:5px;">🎙️ Start Listening</button>
  <button onclick="stopListening()" style="font-size:18px;padding:10px 20px;margin:5px;">🛑 Stop Listening</button>
  <p id="result" style="font-size:20px; margin-top:20px;">...</p>
</div>

<script>
  var recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = true;

  function startListening() {
    recognition.start();
    document.getElementById("result").innerText = "🎙️ Listening...";
  }

  function stopListening() {
    recognition.stop();
  }

  recognition.onresult = function(event) {
    var transcript = event.results[event.results.length - 1][0].transcript;
    document.getElementById("result").innerText = "✅ You said: " + transcript;

    // Send transcript to Streamlit
    const streamlitInput = window.parent.document.querySelector('iframe[srcdoc*="You said"]').closest('iframe');
    streamlitInput.contentWindow.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: transcript }, "*");
  };

  recognition.onerror = function(event) {
    document.getElementById("result").innerText = "❌ Error: " + event.error;
  };
</script>
"""

# Create the voice component
voice_text = components.html(html_code, height=250)

