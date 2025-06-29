from ba_dashboard import gradio_dashboard

# Create the Gradio app
demo = gradio_dashboard()

# Launch the app (this will be used by Hugging Face Spaces)
if __name__ == "__main__":
    demo.launch()
