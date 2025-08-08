import streamlit as st
import ollama

# Set the title of the Streamlit app
st.title("🤖 Ollama Chat")

# --- Configuration ---
st.sidebar.header("Configuration")
# Add a text input in the sidebar for the Ollama host
ollama_host = st.sidebar.text_input("Ollama Host", value="http://localhost:11434")

# --- Model Selection ---
try:
    # Create an Ollama client with the specified host
    client = ollama.Client(host=ollama_host)
    
    # Get the list of models from the client
    models_info = client.list()
    model_names = [model.model for model in models_info['models']]

    # A select box to choose the model
    selected_model = st.selectbox("Choose an Ollama model", model_names)

except Exception as e:
    st.error(f"Could not connect to Ollama at '{ollama_host}'. Please make sure Ollama is running and the host is correct.")
    st.error(f"Error details: {e}")
    # Stop the app if we can't connect to Ollama
    st.stop()

# --- Chat History Initialization ---
# Initialize the chat history in Streamlit's session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
# Loop through the existing messages in the session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Chat Logic ---
# Get user input from the chat input box
if prompt := st.chat_input("What would you like to ask?"):
    # Add the user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the user's message in the chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the assistant's response
    with st.chat_message("assistant"):
        try:
            # Create a generator for the streaming response from Ollama
            def stream_ollama_response():
                # Use the client to stream the chat response
                stream = client.chat(
                    model=selected_model,
                    messages=st.session_state.messages,
                    stream=True,
                )
                # Yield the content of each chunk as it is received
                for chunk in stream:
                    yield chunk['message']['content']

            # Use st.write_stream to display the streamed content
            response = st.write_stream(stream_ollama_response)

            # Add the full response from the assistant to the chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"An error occurred while communicating with Ollama: {e}")
