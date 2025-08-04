# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10.8-slim-buster

# Environment
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Python packages
RUN apt update && \
    apt upgrade -y && \
    apt install -y git && \
    pip install --no-cache-dir -U pip

# Create working directory and copy code
WORKDIR /VJ-Video-Player
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run the bot
CMD ["python3", "bot.py"]
