"""Envia o resumo Focus mais recente por e-mail via Gmail SMTP."""

from __future__ import annotations

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


DESTINATARIO = "a22braga@gmail.com"


def _html_mais_recente() -> Path:
    pasta = Path(__file__).parent.parent / "output" / "focus"
    htmls = sorted(pasta.glob("focus_*.html"))
    if not htmls:
        print("Erro: nenhum HTML encontrado em output/focus/.", file=sys.stderr)
        sys.exit(1)
    return htmls[-1]


def enviar() -> None:
    usuario = os.environ["GMAIL_USER"]
    senha = os.environ["GMAIL_APP_PASSWORD"]

    html_path = _html_mais_recente()
    corpo_html = html_path.read_text(encoding="utf-8")

    # Extrai a data do nome do arquivo (focus_AAAA-MM-DD.html)
    data = html_path.stem.replace("focus_", "")

    assunto_base = f"Resumo Focus — {data}"
    # Propaga o prefixo [REVISAR] se o HTML já o contiver
    if "[REVISAR]" in corpo_html:
        assunto = f"[REVISAR] {assunto_base}"
    else:
        assunto = assunto_base

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = usuario
    msg["To"] = DESTINATARIO
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(usuario, senha)
        smtp.sendmail(usuario, DESTINATARIO, msg.as_string())

    print(f"E-mail enviado: {assunto} → {DESTINATARIO}")


if __name__ == "__main__":
    enviar()
