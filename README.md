# 🎖️ Multi-Agent WW2 Tutor (CrewAI + OpenAI)

Een intelligente geschiedenis-assistent die gebruikmaakt van AI-agenten om vragen over de Tweede Wereldoorlog te beantwoorden.

Dit project gebruikt:
- **CrewAI** voor de orchestratie van meerdere agenten (Researcher & Tutor).
- **OpenAI (GPT-4o-mini)** als de backend LLM.
- Een lokale tekstbasis (`ww2_history_notes.txt`) als kennisbron.
- **Streamlit** voor een gebruiksvriendelijke webinterface.

## 👥 Team
- Natan Wojtowicz
- Tuur Mentens
- Tijl Cleynhens

## 🚀 Quickstart

### 1. Installatie

Zorg dat je Python geïnstalleerd hebt en voer de volgende commando's uit in je terminal:

```bash
# Ga naar de projectmap
cd NLP_Machine_Learning

# Maak een virtual environment aan (optioneel maar aanbevolen)
python -m venv .venv
source .venv/bin/activate  # Op Windows gebruik: .venv\Scripts\activate

# Installeer de vereiste packages
pip install -r requirements.txt