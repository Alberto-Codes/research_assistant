"""
Simplified Streamlit app for testing.
"""
import streamlit as st

# Basic Streamlit UI
st.set_page_config(
    page_title="Hello World Graph - Test",
    page_icon="👋",
    layout="centered"
)

st.title("Hello World Graph - Test")
st.markdown("""
This is a simplified test app to verify Streamlit is working correctly.
""")

# Configuration options in sidebar
st.sidebar.header("Configuration")
use_custom_llm = st.sidebar.checkbox("Use Custom LLM Client", value=True)
prefix = st.sidebar.text_input("Prefix for generated text", value="")

# Generate button
if st.button("Generate Hello World", type="primary"):
    # Direct output without dependencies
    hello_text = f"{prefix} Hello" if prefix else "Hello"
    world_text = f"{prefix} World" if prefix else "World"
    combined_text = f"{hello_text} {world_text}!"
    
    # Display results
    st.success(f"Final output: {combined_text}")
    
    # Display timing information
    st.subheader("Sample Timing Information")
    st.markdown("- Hello generation: **0.100s**")
    st.markdown("- World generation: **0.200s**")
    st.markdown("- Combine operation: **0.150s**")
    st.markdown("- Total time: **0.450s**")
    
    # Display state
    st.subheader("Sample State")
    st.json({
        "hello_text": hello_text,
        "world_text": world_text,
        "combined_text": combined_text
    }) 