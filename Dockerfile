FROM python:3.13-alpine

WORKDIR /app

ARG ODOO_URL
ARG ODOO_DB
ARG ODOO_USERNAME
ARG ODOO_PASSWORD

ENV ODOO_URL=${ODOO_URL}
ENV ODOO_DB=${ODOO_DB}
ENV ODOO_USERNAME=${ODOO_USERNAME}
ENV ODOO_PASSWORD=${ODOO_PASSWORD}

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]