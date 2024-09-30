# Use Ubuntu 22.04 base image
FROM ubuntu:22.04

# Update package lists
RUN apt update

# Install software
RUN apt install -y python3 python3-pip nano 

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

# Expose port 7004 for web traffic
EXPOSE 7004

# Start pyhton app in the foreground
CMD ["python3", "/app/app.py"]