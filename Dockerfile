# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project
COPY . .

# Optional: set default command (Prefect will override this anyway)
CMD ["python", "etl.py"]
