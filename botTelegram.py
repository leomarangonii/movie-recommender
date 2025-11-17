import logging
import os

import requests
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, NetworkError


load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LLAMA_ENDPOINT = "http://localhost:11434/api/chat"
LLAMA_MODEL = "llama3"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def call_llama(prompt: str) -> str:
    payload = {
        "model": LLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um especialista em cinema. "
                    "Seu trabalho é recomendar filmes em português brasileiro."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    resp = requests.post(LLAMA_ENDPOINT, json=payload, timeout=180)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"]

def recommend_with_llama(user_text: str) -> str:

    system_prompt = (
        "Você é um especialista em cinema. "
        "Seu trabalho é recomendar filmes em resposta ao pedido do usuário.\n\n"
        "REGRAS IMPORTANTES:\n"
        "- Responda SEMPRE em português brasileiro.\n"
        "- Seu foco é APENAS filmes (e, se fizer sentido, séries). Você NÃO deve responder "
        "perguntas de matemática, programação, notícias, vida pessoal, etc.\n"
        "- Se o pedido NÃO estiver relacionado a filmes ou séries para assistir, "
        "NÃO tente ajudar com o assunto. Em vez disso, responda com UMA frase curta como:\n"
        "  'Sou um bot feito só para recomendar filmes. Me conta que tipo de filme você quer ver?'\n"
        "- Quando o pedido for sobre filmes/séries, dê de 3 a 5 recomendações.\n"
        "- Para cada filme, informe: título em português (se souber), "
        "título original (se for diferente) e ano entre parênteses.\n"
        "- Embaixo de cada filme, escreva 1 ou 2 frases explicando por que ele "
        "combina com o pedido do usuário.\n"
        "- Só recomende filmes que realmente existam e sejam razoavelmente conhecidos. "
        "Evite inventar filmes com títulos aleatórios.\n"
        "- Se o pedido for muito específico e você não lembrar de nada perfeito, "
        "recomende filmes próximos da ideia e explique isso na justificativa.\n"
        "- Não faça listas enormes nem use markdown complexo. Use apenas texto simples.\n"
        "- Não mencione que você é um modelo de linguagem."
    )

    user_prompt = (
        f"Pedido do usuário:\n\"{user_text}\"\n\n"
        "Agora responda NO SEGUINTE FORMATO de texto simples:\n"
        "1) Título em português / Título original (Ano)\n"
        "   Breve justificativa de 1 ou 2 frases.\n"
        "2) ...\n"
        "3) ...\n"
        "Se achar adequado, pode sugerir até 5 filmes no máximo."
    )

    full_prompt = system_prompt + "\n\n" + user_prompt

    try:
        resposta = call_llama(full_prompt)
        return resposta.strip()
    except Exception as e:
        logger.exception("Erro ao chamar LLaMA para recomendação: %s", e)
        return (
            "Tive um problema para gerar recomendações agora 😥\n"
            "Tenta mandar o pedido de novo em alguns segundos."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    text = (
        f"Olá, {user_first_name}! 🍿\n\n"
        "Eu sou um bot que recomenda filmes usando um modelo de IA (LLaMA).\n"
        "Me conte o que você quer assistir, por exemplo:\n\n"
        " - 'Quero uma comédia romântica leve'\n"
        " - 'Filme de terror psicológico dos anos 80'\n"
        " - 'Um musical sobre circo'\n"
        " - 'Filme de ação com clima mais sério'\n\n"
        "E eu te sugiro alguns títulos 🙂"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 Como usar o bot de filmes\n\n"
        "Basta escrever em linguagem natural o tipo de filme que você quer.\n\n"
        "Exemplos:\n"
        " - 'filme de comédia de 2010 pra cima'\n"
        " - 'drama bem pesado sobre guerra'\n"
        " - 'animação divertida pra ver com crianças'\n"
        " - 'algo parecido com Interestelar'\n\n"
        "Eu vou usar a IA para sugerir alguns filmes que combinem com o seu pedido."
    )
    await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    logger.info("Mensagem do usuário: %s", user_text)

    reply = recommend_with_llama(user_text)
    await update.message.reply_text(reply)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(
        "Erro no update %s: %r",
        getattr(update, "update_id", None),
        context.error,
    )

    err = context.error
    if isinstance(err, (TimedOut, NetworkError)):
        logger.warning("Problema de rede ao falar com a API do Telegram.")

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não encontrado no .env")

    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=20.0,
    )

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
