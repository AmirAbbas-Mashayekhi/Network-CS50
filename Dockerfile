FROM python:3.11-slim

# Install necessary system dependencies for building Python packages like mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./

# Install Python dependencies as root
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and switch to it
RUN addgroup --system app && adduser --system --ingroup app app
USER app

# Copy the rest of the application files
COPY . .

# Run the Django development server
CMD ["python", "manage.py", "runserver"]

EXPOSE 8000
