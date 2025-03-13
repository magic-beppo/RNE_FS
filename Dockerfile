# Use an official Python runtime as the parent image
FROM python:3.10.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Run app.py when the container launches
CMD ["python", "Display_module_1.py"]
