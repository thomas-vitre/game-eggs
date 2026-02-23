import os
import json
import time
import google.generativeai as genai

# Configuration de l'API Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas définie.")
    exit(1)

genai.configure(api_key=API_KEY)

# Utilisation du modèle Flash qui est rapide et adapté aux traductions
model = genai.GenerativeModel('gemini-2.5-flash')

# Dossiers à ignorer (pour ne pas traduire les fichiers de config GitHub ou Git)
EXCLUDED_DIRS = ['.git', '.github']

def translate_with_gemini(text: str, context_type: str) -> str:
    """Envoie le texte à l'API Gemini avec un prompt spécifique au format."""
    if not text or not text.strip():
        return text

    if context_type == "markdown":
        prompt = (
            "Tu es un traducteur expert technique. Traduis le texte Markdown suivant en français. "
            "RÈGLE CRITIQUE : Tu DOIS conserver exactement la même structure Markdown, les balises HTML, "
            "les blocs de code (```), les URLs et les liens intacts. Ne traduis pas le code informatique, "
            "seulement le texte lisible par l'humain. Ne renvoie que le texte traduit sans aucune introduction.\n\n"
            f"{text}"
        )
    elif context_type == "json_description":
        prompt = (
            "Tu es un traducteur expert. Traduis le texte suivant en français. "
            "Ce texte provient d'un champ 'description' d'un fichier JSON de configuration. "
            "Ne renvoie QUE la traduction brute, sans guillemets ajoutés ni commentaires.\n\n"
            f"{text}"
        )
    else:
        return text

    try:
        response = model.generate_content(prompt)
        # Petite pause pour éviter de toucher les limites de requêtes (Rate Limiting) de l'API gratuite
        time.sleep(2) 
        if response.text:
            return response.text.strip()
        return text
    except Exception as e:
        print(f"Erreur lors de la traduction : {e}")
        return text # En cas d'erreur, on retourne le texte original pour ne rien casser

def process_markdown(filepath: str):
    """Lit, traduit et sauvegarde un fichier Markdown."""
    print(f"Traduction du fichier Markdown : {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    translated_content = translate_with_gemini(content, "markdown")

    if translated_content and translated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(translated_content)

def process_json_data(data):
    """Parcourt récursivement un objet JSON pour traduire les clés 'description'."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() == "description" and isinstance(value, str):
                data[key] = translate_with_gemini(value, "json_description")
            else:
                data[key] = process_json_data(value)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = process_json_data(data[i])
    return data

def process_json_file(filepath: str):
    """Lit, traduit les descriptions et sauvegarde un fichier JSON."""
    print(f"Analyse du fichier JSON : {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated_data = process_json_data(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # indent=4 permet de conserver une belle structure JSON
            json.dump(translated_data, f, indent=4, ensure_ascii=False)
            
    except json.JSONDecodeError:
        print(f"Ignoré (JSON invalide) : {filepath}")

def main():
    """Point d'entrée du script qui parcourt le répertoire."""
    # On commence à la racine du dépôt
    root_dir = "." 
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclure les dossiers non désirés
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            if filename.endswith(".md"):
                process_markdown(filepath)
            elif filename.endswith(".json"):
                process_json_file(filepath)

if __name__ == "__main__":
    main()
