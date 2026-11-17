#after refactorization

import json
from pathlib import Path
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown 
from rich.live import Live


MODEL = "gemma4:26b-a4b"
BASE_URL = "http://localhost:11434/v1" 
client = OpenAI(base_url=BASE_URL, api_key="ollama")
HISTORY_FILE = Path("history.json")
myconsole = Console()

def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    else:
        return []

def save_history():
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8") 

def ask_model(history):
    chunks = client.chat.completions.create(
        model=MODEL,
        messages=history,
        stream=True,
        reasoning_effort="none",
    )

    reply = ""
    myconsole.print("[bold cyan]Darwin:[/]")
    with Live(console=myconsole, refresh_per_second=10, vertical_overflow="visible") as live:
        for chunk in chunks:
            # if (chunk.choices):
            #     print(chunk.choices[0].delta)
            # else: 
            #     print("EMPTY LIST")    #debugging purposes
            if chunk.choices and chunk.choices[0].delta.content:
                reply += chunk.choices[0].delta.content
                live.update(Markdown(reply))
    return reply

history = load_history() #history is used above in save_history, but that code only runs when save_history() is called at the end of the loop
while True:
    user_text = input("You: ")
    if user_text == "exit":
        break
    if user_text.strip() == "":
        continue #continue skips the rest of the loop and goes back to the beginning of the loop

    history.append({"role": "user", "content": user_text})
    
    reply = ask_model(history)
    if reply == "":
        myconsole.print("[bold red]No response from the model.[/]")
        history.pop() #pop is a list method that removes the last item from the list, in this case the last user input that didn't get the response
        continue
    history.append({"role": "assistant", "content": reply})
    save_history()

