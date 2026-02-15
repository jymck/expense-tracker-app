FROM python:3.11-slim

WORKDIR /app

# Copy all files
COPY . .

# Port that the app runs on
EXPOSE 3000

# Run the server
CMD ["python", "server.py"]
