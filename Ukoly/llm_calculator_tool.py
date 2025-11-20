import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Jan Šrámko (War-cry), prosím o kontrolu a schovívavost nejsem programátor ;)
# Načtení proměnných prostředí (.env)
load_dotenv()

client = OpenAI()

# 1. Definice naší "výpočetní" funkce v Pythonu
def calculate(a: float, b: float, operation: str) -> float:
    """
    Provede základní matematickou operaci se dvěma čísly.
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return 0  # Zjednodušení pro demo
        return a / b
    else:
        raise ValueError("Unknown operation")

# 2. Definice nástroje (Tool) pro OpenAI (JSON Schema)
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "A simple calculator for basic operations (add, subtract, multiply, divide).",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The first number."
                    },
                    "b": {
                        "type": "number",
                        "description": "The second number."
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The operation to perform."
                    }
                },
                "required": ["a", "b", "operation"]
            }
        }
    }
]

def run_conversation():
    # 3. Položení dotazu modelu
    # Záměrně "složitější" dotaz, aby model musel volat funkci (možná i vícekrát, nebo postupně)
    # použil jsem slovo "krát" jestli to funguje. Funguje i když dám "x" místo "krát".
    user_query = "Kolik je 123 krát 45?"
    print(f"User: {user_query}")

    messages = [{"role": "user", "content": user_query}]

    # První volání API - model by měl rozpoznat, že potřebuje použít nástroj
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto", 
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 4. Pokud model chce volat funkci...
    if tool_calls:
        print(f"Model se rozhodl použít nástroj (tool call)...")
        
        # Přidáme odpověď modelu (s požadavkem na funkci) do historie konverzace
        messages.append(response_message)

        # Mapování názvů funkcí na skutečné Python funkce
        available_functions = {
            "calculate": calculate,
        }

        # Projdeme všechny tool calls
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            print(f" -> Volám Python funkci '{function_name}' s argumenty: {function_args}")
            
            # Spuštění funkce
            function_response = function_to_call(
                a=function_args.get("a"),
                b=function_args.get("b"),
                operation=function_args.get("operation"),
            )
            
            print(f" -> Výsledek z Pythonu: {function_response}")

            # 5. Vrácení výsledku zpět modelu
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )

        # 6. Druhé volání API - model dostane výsledek a zformuje finální odpověď
        print("Posílám výsledek zpět modelu pro finální odpověď...")
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        
        print(f"\nAI: {second_response.choices[0].message.content}")
    else:
        print("Model se rozhodl nepoužít žádný nástroj a odpověděl přímo.")
        print(f"AI: {response_message.content}")

if __name__ == "__main__":
    run_conversation()
