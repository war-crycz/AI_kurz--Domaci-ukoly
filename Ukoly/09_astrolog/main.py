import asyncio
import os
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# Cesta ke složce kde je tento soubor (main.py)
SCRIPT_DIR = Path(__file__).parent.resolve()
ENV_FILE = SCRIPT_DIR / ".env"

# Načti .env ze složky projektu
load_dotenv(dotenv_path=ENV_FILE, override=False)

print(f"📂 Složka projektu: {SCRIPT_DIR.parent}") 
print(f"📄 Hledám .env: {ENV_FILE}")


# === HELPER: Normalizace data ===
def normalize_date(birth_date: str) -> str:
    """Převede datum do formátu dd.mm.rrrr (doplní nuly)."""
    try:
        parts = birth_date.strip().split(".")
        day = parts[0].zfill(2)
        month = parts[1].zfill(2)
        year = parts[2]
        return f"{day}.{month}.{year}"
    except (ValueError, IndexError):
        return birth_date  # Vrať originál pokud selže


# === PAMĚŤ - seznam uživatelů ===
users_memory: list[dict] = []


def get_current_date() -> str:
    """
    Vrátí aktuální datum a čas. VŽDY použij tento nástroj pro zjištění dnešního data!
    """
    today = date.today()
    days_cz = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
    day_name = days_cz[today.weekday()]
    return f"Dnes je {day_name} {today.strftime('%d.%m.%Y')}"


def save_user(name: str, birth_date: str) -> str:
    """
    Uloží nového uživatele do paměti (jméno a datum narození).
    """
    normalized_date = normalize_date(birth_date)
    
    # Spočítej dny na světě
    try:
        parts = normalized_date.split(".")
        birth = date(int(parts[2]), int(parts[1]), int(parts[0]))
        days_alive = (date.today() - birth).days
    except:
        days_alive = 0
    
    user = {
        "name": name,
        "birth_date": normalized_date,
        "days_alive": days_alive
    }
    users_memory.append(user)
    
    return f"✅ Uloženo: {name}, narozen/a {normalized_date} ({days_alive} dní)"


def list_all_users() -> str:
    """
    Zobrazí seznam všech uložených uživatelů v paměti.
    """
    if not users_memory:
        return "📭 Paměť je prázdná. Zatím nebyl uložen žádný uživatel."
    
    result = f"📋 Uložení uživatelé ({len(users_memory)}):\n"
    for i, user in enumerate(users_memory, 1):
        result += f"  {i}. {user['name']} - {user['birth_date']} ({user['days_alive']} dní)\n"
    
    return result


def get_total_days() -> str:
    """
    Spočítá celkový součet dní na světě všech uložených uživatelů.
    """
    if not users_memory:
        return "📭 Paměť je prázdná. Nelze spočítat součet."
    
    total = sum(user["days_alive"] for user in users_memory)
    count = len(users_memory)
    
    return f"📊 Celkem {count} uživatelů = {total:,} dní dohromady!".replace(",", " ")


def clear_memory() -> str:
    """
    Vymaže všechny uložené uživatele z paměti.
    """
    count = len(users_memory)
    users_memory.clear()
    return f"🗑️ Paměť vymazána. Odstraněno {count} uživatelů."


# === ZNAMENÍ ZVĚROKRUHU ===
def get_zodiac_sign(birth_date: str) -> str:
    """
    Určí znamení zvěrokruhu podle data narození.
    """
    birth_date = normalize_date(birth_date)
    try:
        parts = birth_date.split(".")
        day = int(parts[0])
        month = int(parts[1])
    except (ValueError, IndexError):
        return "Neplatný formát data. Použij dd.mm.rrrr"
    
    zodiac_signs = [
        ((1, 20), (2, 18), "Vodnář ♒"),
        ((2, 19), (3, 20), "Ryby ♓"),
        ((3, 21), (4, 19), "Beran ♈"),
        ((4, 20), (5, 20), "Býk ♉"),
        ((5, 21), (6, 20), "Blíženci ♊"),
        ((6, 21), (7, 22), "Rak ♋"),
        ((7, 23), (8, 22), "Lev ♌"),
        ((8, 23), (9, 22), "Panna ♍"),
        ((9, 23), (10, 22), "Váhy ♎"),
        ((10, 23), (11, 21), "Štír ♏"),
        ((11, 22), (12, 21), "Střelec ♐"),
        ((12, 22), (1, 19), "Kozoroh ♑"),
    ]
    
    for start, end, sign in zodiac_signs:
        if start[0] == end[0]:  # Stejný měsíc
            if month == start[0] and start[1] <= day <= end[1]:
                return sign
        elif start[0] == 12 and end[0] == 1:  # Kozoroh (prosinec-leden)
            if (month == 12 and day >= start[1]) or (month == 1 and day <= end[1]):
                return sign
        else:
            if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
                return sign
    
    return "Neznámé znamení"


# === VÝPOČET VĚKU ===
def calculate_age(birth_date: str) -> str:
    """
    Spočítá přesný věk uživatele v letech, měsících a dnech.
    """
    birth_date = normalize_date(birth_date)
    try:
        parts = birth_date.split(".")
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
        birth = date(year, month, day)
    except (ValueError, IndexError):
        return "Neplatný formát data. Použij dd.mm.rrrr"
    
    today = date.today()
    
    # Výpočet let, měsíců, dní
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day
    
    if days < 0:
        months -= 1
        # Počet dní v předchozím měsíci
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        days_in_prev_month = (date(prev_year, prev_month + 1, 1) - date(prev_year, prev_month, 1)).days if prev_month < 12 else 31
        days += days_in_prev_month
    
    if months < 0:
        years -= 1
        months += 12
    
    # Celkový počet dní
    total_days = (today - birth).days
    
    return f"Věk: {years} let, {months} měsíců a {days} dní. Celkem {total_days:,} dní na tomto světě!".replace(",", " ")


# === ČÍNSKÝ HOROSKOP ===
def get_chinese_zodiac(birth_date: str) -> str:
    """
    Určí čínské zvířecí znamení podle roku narození.
    """
    birth_date = normalize_date(birth_date)
    try:
        year = int(birth_date.split(".")[2])
    except (ValueError, IndexError):
        return "Neplatný formát data. Použij dd.mm.rrrr"
    
    animals = [
        ("Opice 🐵", "Chytří, zvědaví a hraví"),
        ("Kohout 🐓", "Pracovití, odvážní a talentovaní"),
        ("Pes 🐕", "Loajální, čestní a přátelští"),
        ("Vepř 🐷", "Štědří, soucitní a pilní"),
        ("Krysa 🐀", "Chytří, šarmantní a ambiciózní"),
        ("Buvol 🐂", "Spolehliví, silní a odhodlaní"),
        ("Tygr 🐅", "Odvážní, konkurenceschopní a sebevědomí"),
        ("Králík 🐇", "Tiší, elegantní a laskaví"),
        ("Drak 🐉", "Sebevědomí, inteligentní a nadšení"),
        ("Had 🐍", "Moudří, záhadní a intuitivní"),
        ("Kůň 🐎", "Energičtí, nezávislí a netrpěliví"),
        ("Koza 🐐", "Klidní, jemní a soucitní"),
    ]
    
    index = (year - 1900) % 12
    animal, traits = animals[index]
    
    return f"Čínské znamení: {animal} - {traits}"


# === NUMEROLOGIE ===
def calculate_life_number(birth_date: str) -> str:
    """
    Spočítá životní číslo podle numerologie.
    """
    birth_date = normalize_date(birth_date)
    try:
        parts = birth_date.split(".")
        digits = "".join(parts)
        
        # Sečti všechny číslice dokud nezůstane jednociferné číslo
        total = sum(int(d) for d in digits)
        while total > 9 and total not in [11, 22, 33]:  # Mistrovská čísla
            total = sum(int(d) for d in str(total))
    except (ValueError, IndexError):
        return "Neplatný formát data. Použij dd.mm.rrrr"
    
    meanings = {
        1: "Vůdce - nezávislý, ambiciózní, originální",
        2: "Diplomat - citlivý, spolupracující, mírumilovný",
        3: "Tvůrce - kreativní, expresivní, optimistický",
        4: "Stavitel - praktický, organizovaný, spolehlivý",
        5: "Dobrodruh - svobodomyslný, všestranný, zvědavý",
        6: "Pečovatel - zodpovědný, milující, ochranitelský",
        7: "Myslitel - analytický, introspektivní, duchovní",
        8: "Achiever - ambiciózní, materialistický, mocný",
        9: "Humanista - soucitný, idealistický, velkorysý",
        11: "Mistr Intuice - vizionář, inspirativní, duchovní",
        22: "Mistr Stavitel - praktický vizionář, mocný",
        33: "Mistr Učitel - soucitný, moudrý, duchovní průvodce",
    }
    
    meaning = meanings.get(total, "Neznámý význam")
    return f"Životní číslo: {total} - {meaning}"


# === INSTRUKCE PRO AGENTY ===
LOGIC_INSTRUCTIONS = """
Jsi přátelský český astrolog a numerolog.
Tvým úkolem je analyzovat data o uživateli pomocí dostupných Python nástrojů.

## PŘÍKAZY PRO JMÉNO A DATUM NAROZENÍ (např. "Jan 1.1.1980"):
MUSÍŠ zavolat VŠECHNY tyto nástroje:
1. save_user(jméno, datum)
2. get_zodiac_sign(datum)
3. calculate_age(datum)
4. get_chinese_zodiac(datum)
5. calculate_life_number(datum)

## SPECIÁLNÍ PŘÍKAZY (ALIASY):
- Pokud uživatel napíše "seznam" nebo "list" -> VŽDY zavolej list_all_users()
- Pokud uživatel napíše "součet" nebo "total" -> VŽDY zavolej get_total_days()
- Pokud uživatel napíše "vymazat" nebo "clear" -> VŽDY zavolej clear_memory()

Datum předávej ve formátu dd.mm.rrrr.
"""

WEB_INSTRUCTIONS = """
Jsi expert na vyhledávání svátků v českém kalendáři.
Tvým úkolem je zjistit, kdy má JMENINY (svátek) zadané jméno.

POSTUP:
1. VŽDY použij "Web Browser".
2. Hledej dotaz: "Kdy má svátek {jméno} svatky.centrum.cz"
3. Otevři relevantní výsledek a najdi datum.
4. Pozor na záměnu s "January" (anglicky Leden). Hledáš jméno "Jan" (mužské jméno).
5. Odpověz POUZE pokud jsi informaci našel na webu.
"""


async def main():
    # === KONTROLA API KLÍČE ===
    env_file_key = None
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value: env_file_key = value; break
    
    system_key = os.getenv("OPENAI_API_KEY")
    api_key = env_file_key or system_key
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        key_source = "📁 soubor .env" if env_file_key else "🖥️  systémová proměnná"
    else:
        print("❌ CHYBA: OPENAI_API_KEY chybí!")
        return
    
    if not api_key.startswith("sk-"):
        print(f"⚠️  VAROVÁNÍ: API klíč nevypadá správně (měl by začínat 'sk-')")
        print(f"   Zdroj: {key_source}")
    else:
        print(f"✅ API klíč nalezen: {api_key[:12]}...{api_key[-4:]}")
        print(f"   Zdroj: {key_source}")

    # === KONTROLA MCP ===
    print("🔌 MCP server (Playwright):")
    mcp_url = "http://localhost:8931"
    try:
        req = urllib.request.Request(mcp_url, method='GET')
        with urllib.request.urlopen(req, timeout=3) as r:
            print(f"   ✅ Běží (status: {r.status})")
    except urllib.error.HTTPError as e:
        if e.code in [400, 404, 405]:
             print(f"   ✅ Běží (odpověděl: {e.code})")
        else:
            print(f"   ⚠️  Možný problém s MCP: {e}")
    except Exception as e:
        print(f"   ⚠️  Možný problém s MCP: {e}")

    print("-" * 60)
    
    # === MODELY A AGENTI ===
    model = OpenAIChatClient(model_id="gpt-4o-mini")
    
    # 1. LOGICKÝ AGENT (persistentní)
    logic_tools = [
        get_current_date, save_user, list_all_users, get_total_days, 
        clear_memory, get_zodiac_sign, calculate_age, 
        get_chinese_zodiac, calculate_life_number
    ]
    logic_agent = ChatAgent(
        chat_client=model,
        instructions=LOGIC_INSTRUCTIONS,
        tools=logic_tools,
        tool_choice="auto"
    )

    # 2. WEB AGENT (Tool definition only, agent created per request)
    mcp_tool = MCPStreamableHTTPTool(name="Web Browser", url="http://localhost:8931")
    
    # Přivítání
    print("=" * 60)
    print("🌟 OSOBNÍ ASTROLOG A NUMEROLOG 🌟")
    print("=" * 60)
    print("\nZadej jméno a datum narození (dd.mm.rrrr)")
    print("Příklad: Marek 22.08.1990")
    print("\n📋 Příkazy:")
    print("  • seznam / list    - zobrazí všechny uložené osoby")
    print("  • součet / total   - celkový počet dní všech osob")
    print("  • vymazat / clear  - vymaže paměť")
    print("  • konec / exit     - ukončí program")
    print("-" * 60)

    # === HLAVNÍ SMYČKA ===
    async with logic_agent: # Logic agent is persistent
        while True:
            user_input = input("\n👤 Ty: ").strip()
            if user_input.lower() in ["konec", "exit", "q"]:
                print("\n👋 Nashledanou!")
                break
            if not user_input:
                continue

            print("\n⏳ Zpracovávám...")

            try:
                # === ORCHESTRACE ===
                
                # A) Jméno a datum (komplexní analýza)
                if any(c.isdigit() for c in user_input) and "." in user_input:
                    # 1. Logic Agent
                    print("🔮 Spouštím astrologickou analýzu...")
                    logic_result = await logic_agent.run(user_input)
                    
                    # 2. Web Agent (stateless)
                    name = user_input.split()[0]
                    print(f"🌐 Hledám svátek pro: {name}...")
                    
                    # Vytvoření nového agenta pro každý request (čistý stav)
                    web_agent = ChatAgent(
                        chat_client=model,
                        instructions=WEB_INSTRUCTIONS,
                        tools=[mcp_tool] # List!
                    )
                    async with web_agent:
                        web_result = await web_agent.run(f"Kdy má svátek {name}? A co to jméno znamená?")
                    
                    # 3. Výpis
                    print("\n🤖 Asistent (Astrologie):")
                    print("-" * 40)
                    print(logic_result.text)
                    print("\n🤖 Asistent (Web):")
                    print("-" * 40)
                    print(web_result.text)
                    print("-" * 60)

                # B) Dotaz na svátek/web
                elif any(w in user_input.lower() for w in ["svátek", "jmeniny", "kdy má"]):
                    print("🌐 Spouštím vyhledávání na webu...")
                    # Stateless Web Agent
                    web_agent = ChatAgent(
                        chat_client=model,
                        instructions=WEB_INSTRUCTIONS,
                        tools=[mcp_tool]
                    )
                    async with web_agent:
                        result = await web_agent.run(user_input)
                    print(f"\n🤖 Asistent: {result.text}")
                    print("-" * 60)

                # C) Ostatní (Logic Agent)
                else:
                    result = await logic_agent.run(user_input)
                    print(f"\n🤖 Asistent: {result.text}")
                    print("-" * 60)

            except Exception as e:
                print(f"❌ Chyba: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
