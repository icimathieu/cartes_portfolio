FROM python:3.13.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY src/ ./src/
COPY assets/ ./assets/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# --server.xsrfCookieSameSite=none : le Space est aussi affiché dans un cadre servi
# par huggingface.co. Sans cela le cookie XSRF (SameSite=Lax par défaut) est
# invisible depuis ce cadre, et le téléversement de la page « Essayer » échoue
# en 403. Streamlit y ajoute tout seul l'attribut Secure ; le Space est en HTTPS.
ENTRYPOINT ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.xsrfCookieSameSite=none"]
