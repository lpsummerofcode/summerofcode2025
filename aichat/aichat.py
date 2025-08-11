import streamlit as st
import ollama

# --- Page Configuration ---
st.set_page_config(page_title="🤖 Ollama Chat", layout="wide")

# --- State Management ---
# Initialize session state variables if they don't exist
if "selected_bot_name" not in st.session_state:
    # Default bot that acts as a general assistant
    default_bot = {"name": "Ollama Assistant", "description": "You are a helpful assistant."}
    st.session_state.bots = {"Ollama Assistant": default_bot}
    st.session_state.selected_bot_name = "Ollama Assistant"
    # Store messages in a nested dictionary, one list per bot
    st.session_state.messages = {"Ollama Assistant": []}

# --- Helper Functions ---
def reset_current_chat():
    """Resets the chat history for the currently selected bot."""
    bot_name = st.session_state.selected_bot_name
    st.session_state.messages[bot_name] = []

# --- Sidebar ---
st.sidebar.header("Configuration")
ollama_host = st.sidebar.text_input("Ollama Host", value="http://localhost:11434")

# Dropdown to select the active bot
bot_names = list(st.session_state.bots.keys())
st.session_state.selected_bot_name = st.sidebar.selectbox(
    "Choose a Bot", 
    options=bot_names, 
    index=bot_names.index(st.session_state.selected_bot_name),
    key="bot_selector"
)

# Button to clear the chat history for the current bot
st.sidebar.button("Clear Chat History", on_click=reset_current_chat, use_container_width=True)

# --- Main UI ---
# Use columns to place the title and the "Add Bot" button on the same line
col1, col2 = st.columns([5, 1])
with col1:
    st.title(f"🤖 {st.session_state.selected_bot_name}")
with col2:
    # Placeholder for the button to align it to the right
    st.write("") 
    if st.button("➕ Add Bot", use_container_width=True):
        st.session_state.show_add_bot_form = True

# --- "Add Bot" Modal/Form ---
# This form will appear when the 'Add Bot' button is clicked
if st.session_state.get("show_add_bot_form", False):
    with st.form("add_bot_form"):
        st.subheader("Create a New Bot")
        new_bot_name = st.text_input("Bot Name", placeholder="e.g., Pirate Captain")
        new_bot_description = st.text_area(
            "Bot Description (System Prompt)", 
            placeholder="e.g., You are a Pirate Captain. All your responses must be in pirate speak.",
            height=200
        )
        
        # Form submission button
        submitted = st.form_submit_button("Save Bot")
        if submitted:
            if new_bot_name and new_bot_description:
                if new_bot_name not in st.session_state.bots:
                    # Add the new bot to the state
                    st.session_state.bots[new_bot_name] = {"name": new_bot_name, "description": new_bot_description}
                    # Initialize its message history
                    st.session_state.messages[new_bot_name] = []
                    # Switch to the new bot
                    st.session_state.selected_bot_name = new_bot_name
                    st.session_state.show_add_bot_form = False
                    st.rerun() # Rerun the app to update the UI
                else:
                    st.error("A bot with this name already exists.")
            else:
                st.error("Please provide both a name and a description.")

# --- Ollama Connection and Model Selection ---
try:
    client = ollama.Client(host=ollama_host)
    models_info = client.list()
    model_names = [model.model for model in models_info['models']]
    
    # Place model selection in the sidebar under the bot selection
    selected_model = st.sidebar.selectbox("Choose an Ollama model", model_names)

except Exception as e:
    st.error(f"Could not connect to Ollama at '{ollama_host}'. Please make sure Ollama is running and the host is correct.")
    st.error(f"Error details: {e}")
    st.stop()


# --- Chat History Display ---
# Get the messages for the currently selected bot
current_messages = st.session_state.messages[st.session_state.selected_bot_name]

for message in current_messages:
    # We only display user and assistant messages, not the system prompt
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# --- User Input and Chat Logic ---
if prompt := st.chat_input("What would you like to ask?"):
    # Add user's message to the current bot's history
    current_messages.append({"role": "user", "content": prompt})
    
    # Display user's message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for Ollama, including the system prompt
    messages_for_ollama = []
    # Add the system prompt from the bot's description
    bot_description = st.session_state.bots[st.session_state.selected_bot_name]["description"]
    messages_for_ollama.append({"role": "system", "content": bot_description})
    # Add the rest of the conversation
    messages_for_ollama.extend(current_messages)
    
    # Display assistant's response
    with st.chat_message("assistant"):
        try:
            def stream_ollama_response():
                stream = client.chat(
                    model=selected_model,
                    messages=messages_for_ollama,
                    stream=True,
                )
                for chunk in stream:
                    yield chunk['message']['content']

            response = st.write_stream(stream_ollama_response)
            # Add the full response to the current bot's history
            current_messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"An error occurred while communicating with Ollama: {e}")
