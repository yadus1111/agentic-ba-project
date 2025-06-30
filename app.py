import os
import sys
from ba_dashboard import gradio_dashboard

# Set environment variables for Hugging Face Spaces
os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
os.environ.setdefault("GRADIO_SERVER_PORT", "7860")

# Launch the dashboard
if __name__ == "__main__":
    demo = gradio_dashboard()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Disable share for HF Spaces
        show_error=True
    )
