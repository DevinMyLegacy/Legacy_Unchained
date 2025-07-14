# Use a standard Python image as a base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# NEW FIX: Set the home directory to our app's folder.
# This tells Streamlit to write its files here, where it has permission.
ENV HOME=/app

# Copy the requirements file and install the libraries
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
COPY . .

# Tell Hugging Face which port the app will run on
EXPOSE 8501

# The command to start the Streamlit app
# Note: I have also corrected app.py to streamlit_app.py here.
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]