FROM python:3.13

WORKDIR .

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
  && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip \
  && unzip terraform_1.6.6_linux_amd64.zip \
  && mv terraform /usr/bin \
  && rm terraform_1.6.6_linux_amd64.zip

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# RUN pip install "fastapi[standard]"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
