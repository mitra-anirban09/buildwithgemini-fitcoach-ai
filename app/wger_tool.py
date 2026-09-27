"""Wger Exercise Database tool for FitCoach AI (Public API)."""

import urllib.parse
import urllib.request
import json


def search_public_exercise_database(term: str = "") -> str:
    """Search the Wger.de public exercise database for real exercise definitions, muscles worked, and equipment.

    Args:
        term: Search query term to filter exercises (e.g., 'squat', 'bench', 'curl', 'abs').

    Returns:
        Formatted summary string with matching exercises, target muscles, equipment, and category.
    """
    url = "https://wger.de/api/v2/exerciseinfo/?limit=60"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "FitCoachAI-Agent/1.0", "Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return f"Wger API returned HTTP status {response.status}."

            data = json.loads(response.read().decode("utf-8"))
            results = data.get("results", [])

            matches = []
            term_lower = term.lower().strip()

            for item in results:
                # Find exercise translation / name
                translations = item.get("translations", [])
                name = ""
                description = ""

                for trans in translations:
                    if trans.get("language") == 2:  # English
                        name = trans.get("name")
                        description = trans.get("description", "")
                        break

                if not name and translations:
                    name = translations[0].get("name", "")

                category = item.get("category", {}).get("name", "General")
                muscles = [
                    m.get("name_en") or m.get("name")
                    for m in item.get("muscles", [])
                    if m.get("name_en") or m.get("name")
                ]
                equipment = [
                    eq.get("name") for eq in item.get("equipment", []) if eq.get("name")
                ]

                # Filter by term
                if term_lower:
                    searchable = f"{name} {category} {' '.join(muscles)} {' '.join(equipment)}".lower()
                    if term_lower not in searchable:
                        continue

                if name:
                    muscles_str = ", ".join(muscles) if muscles else "Full Body"
                    equip_str = ", ".join(equipment) if equipment else "None / Bodyweight"
                    matches.append(
                        f"• {name} | Category: {category} | Muscles: {muscles_str} | Equipment: {equip_str}"
                    )

            if not matches:
                return f"No exercises found matching '{term}' in Wger public database."

            return f"Found {len(matches[:8])} matching exercises from Wger Public Database:\n" + "\n".join(matches[:8])

    except Exception as e:
        return f"Error querying Wger Exercise API: {e}"
