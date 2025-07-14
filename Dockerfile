# Use a standard Python image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# THE NEW FIX: Manually create the directory Streamlit needs 
# and give it open permissions before the app starts.
RUN mkdir -p /app/.streamlit && chmod -R 777 /app/.streamlit

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