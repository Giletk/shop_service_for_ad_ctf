FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -m -d /home/user -s /usr/sbin/nologin user

RUN mkdir -p /home/user/data && \
    chown -R user:user /home/user/data && \
    chmod 770 /home/user/data

WORKDIR /app

COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/

RUN chown -R user:user /app

USER user

EXPOSE 5000

CMD ["python", "app.py"]
