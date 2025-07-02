FROM python:3.10-slim AS builder 
LABEL stage="builder"

WORKDIR /app 

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt  


# -------- STAGE 2: RUNTIME ----------
FROM python:3.10-slim

WORKDIR /app 

COPY --from=builder /install /usr/local  

COPY . .   

COPY opik.config /app/opik.config

COPY start.sh /app/start.sh 
RUN chmod +x /app/start.sh

RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot
USER nonroot

EXPOSE 8000 

CMD ["/app/start.sh"]