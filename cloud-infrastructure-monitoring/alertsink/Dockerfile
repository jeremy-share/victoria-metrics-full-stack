FROM python:3.9

RUN mkdir -p /opt/project
WORKDIR /opt/project

# Install requirements
COPY requirements.in ./
RUN pip3 install -r requirements.in

# Copy project files
COPY src/ ./src/

# Run the project
CMD ["python", "-m", "src.main"]
