ARG PORT=8000
FROM cypress/browsers:24.11.0

RUN apt-get update && apt-get install -y \
    python3 python3-pip chromium-driver 

WORKDIR /app

COPY requirements.txt .
ENV PATH=/root/.local/bin:${PATH}
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt  

COPY . .
EXPOSE $PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
