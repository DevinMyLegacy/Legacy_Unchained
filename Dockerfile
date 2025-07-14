# # Use a standard Python image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# FIX 1: Manually create the directory Streamlit needs and give it permissions.
RUN mkdir -p /app/.streamlit && chmod -R 777 /app/.streamlit

# FIX 2: Set the cache directory for Hugging Face models to be inside our app folder.
ENV HF_HOME=/app/huggingface_cache

# Copy requirements file first
COPY requirements.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files
COPY . .

# Tell Hugging Face which port the app will run on
EXPOSE 8501

# The command to start the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]