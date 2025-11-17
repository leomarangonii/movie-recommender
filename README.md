# Movie Recommender Bot🎬

Bot do Telegram que recomenda filmes a partir de descrições em **linguagem natural**, usando um modelo de IA **LLaMA** rodando localmente via **Ollama**.

> Projeto desenvolvido para a disciplina de **Sistemas de Recomendação** (USP).

---

## ✨ O que o bot faz?

- Você conversa com o bot pelo Telegram, em português, escrevendo coisas como:
  - `quero uma comédia romântica leve`
  - `filme de terror psicológico dos anos 80`
  - `algo parecido com Interestelar`
- O bot envia esse texto para o modelo LLaMA.
- O LLaMA responde com **3 a 5 filmes recomendados**, cada um com uma **pequena justificativa**.


---

## 🧩 Tecnologias usadas

- **Python 3.10+**
- **[python-telegram-bot](https://python-telegram-bot.org/)**
- **[Ollama](https://ollama.com/)** (para rodar o LLaMA localmente)
- **LLaMA (ex.: `llama3`)**
- `requests`, `python-dotenv`, `httpx`

---
