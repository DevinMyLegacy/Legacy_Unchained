import streamlit as st
import autogen
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- Page Configuration ---
st.set_page_config(
    page_title="Legacy Unchained",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Header ---
st.title("Legacy Unchained ⛓️")
st.info("An experimental AI agent for task automation. I can write and execute code to help with your tasks. Please review and approve all actions.")

# --- Model Loading ---
# This function loads the AI model and tokenizer.
# @st.cache_resource makes it run only once, so the app is fast.
@st.cache_resource(show_spinner="Loading AI Model (this may take a moment)...")
def load_model():
    model_id = "microsoft/Phi-3-mini-4k-instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # The model is loaded to the CPU, as required by the free hosting service.
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="cpu",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    return model, tokenizer

# Load the model and handle potential errors
try:
    model, tokenizer = load_model()
except Exception as e:
    st.error(f"Error loading AI model: {e}")
    st.stop()

# --- AutoGen Configuration ---
# Configure the AI model for AutoGen
config_list = [{
    "model": "phi3-mini-hosted",
    "model_client_cls": "autogen.runtime_logging.CapturingLLM",
    "llm_config": {
        "model": model,
        "tokenizer": tokenizer,
    }
}]

# --- Agent Definitions ---
# The Assistant Agent is the "brain" that creates plans and writes code.
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)

# The User Proxy Agent is the "hands" that executes code after your approval.
# We create a custom version to integrate with Streamlit's buttons.
class MyUserProxyAgent(autogen.UserProxyAgent):
    def get_human_input(self, prompt: str) -> str:
        # When the assistant wants to run code, it sends a prompt.
        # We store this prompt in the session state to display it to the user.
        st.session_state.approval_prompt = prompt
        # We return an empty string to pause the conversation until a button is clicked.
        return ""

user_proxy = MyUserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS", # This ensures it always asks for your approval.
    code_execution_config={
        "work_dir": "coding", # A safe directory for the agent to work in.
        "use_docker": False,
    },
)

# --- Streamlit Chat Interface ---
# Initialize session state for messages and approval prompts
if "messages" not in st.session_state:
    st.session_state.messages = []
if "approval_prompt" not in st.session_state:
    st.session_state.approval_prompt = None

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display the approval box if the agent wants to run code
if st.session_state.approval_prompt:
    prompt_text = st.session_state.approval_prompt
    with st.chat_message("assistant", avatar="🤖"):
        st.warning("The agent wants to run the following code. Please review carefully.")
        # Extract and display the Python code from the prompt
        code_to_run = prompt_text.split("```python")[1].split("```")[0]
        st.code(code_to_run, language="python")

        # Create columns for the buttons
        col1, col2, _ = st.columns([1, 1, 5])
        # The "Approve" button
        if col1.button("✅ Approve", key="approve"):
            user_proxy.send(message="", recipient=assistant) # Send empty message to approve
            st.session_state.approval_prompt = None # Clear the prompt
            st.rerun() # Rerun the app to continue the conversation
        # The "Deny" button
        if col2.button("❌ Deny & Exit", key="deny"):
            user_proxy.send(message="exit", recipient=assistant) # Send "exit" to terminate
            st.session_state.approval_prompt = None # Clear the prompt
            st.rerun() # Rerun the app

# The main chat input box
if chat_input := st.chat_input("What task should I perform?"):
    # Add user's message to the chat log
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)

    # Start the conversation with the agent
    with st.spinner("🤖 The agent is thinking..."):
        user_proxy.initiate_chat(assistant, message=chat_input)
        # Once the chat is paused for approval or finished, rerun the app
        st.rerun()
