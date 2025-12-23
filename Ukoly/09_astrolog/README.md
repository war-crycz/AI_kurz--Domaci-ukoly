# Osobní Astrolog a Numerolog

Konverzační agent postavený na **OpenAI Agent SDK** (`agent-framework`), který analyzuje data narození a poskytuje astrologické/numerologické informace.

## Funkce

- Znamení zvěrokruhu + čínský horoskop
- Výpočet věku a životního čísla (numerologie)
- Vyhledávání svátků na webu (MCP + Playwright)
- In-memory úložiště uživatelů

## Požadavky

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- OpenAI API klíč
- MCP server (volitelně, pro web search)

## Instalace

```bash
# Klonování a přechod do složky
cd projekt

# Instalace závislostí
uv sync

# Nastavení API klíče
echo "OPENAI_API_KEY=sk-..." > .env
```

## Spuštění

```bash
uv run python main.py
```

## Použití

```
👤 Ty: Jan 15.3.1990
🤖 Asistent: Uloženo, znamení Ryby, čínské znamení Kůň...

👤 Ty: seznam
🤖 Asistent: Uložení uživatelé: 1. Jan - 15.03.1990

👤 Ty: konec
```

### Příkazy

| Příkaz | Akce |
|--------|------|
| `Jméno dd.mm.rrrr` | Kompletní analýza |
| `seznam` / `list` | Seznam uživatelů |
| `součet` / `total` | Celkový počet dnů |
| `vymazat` / `clear` | Smazání paměti |
| `konec` / `exit` | Ukončení |

## Architektura

```
┌─────────────────┐     ┌─────────────────┐
│   Logic Agent   │     │    Web Agent    │
│  (persistentní) │     │   (stateless)   │
├─────────────────┤     ├─────────────────┤
│ • save_user     │     │ • MCP/Playwright│
│ • zodiac_sign   │     │ • web search    │
│ • chinese_zodiac│     └────────┬────────┘
│ • life_number   │              │
│ • calculate_age │              │
└────────┬────────┘              │
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌───────────┐
              │GPT-4o-mini│
              └───────────┘
```

## Licence

MIT
