import os
import google.generativeai as genai

# Configuration de Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Extensions à traduire
EXTENSIONS = ['.md', '.json', '.txt']
# Dossiers à ignorer pour ne pas gaspiller de quota
IGNORE_DIRS = ['.git', '.github', 'node_modules', 'venv']

def translate_content(content, filename):
    prompt = f"""Tu es un traducteur expert en développement logiciel. 
    Traduis le contenu suivant en Français.
    CONSIGNES :
    1. Garde les balises HTML, les clés JSON et la syntaxe Markdown intactes.
    2. Ne traduis pas les termes techniques (ex: 'egg', 'docker', 'commit').
    3. Si c'est du code, ne traduis que les commentaires.
    
    NOM DU FICHIER : {filename}
    CONTENU :
    {content}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erreur sur {filename}: {e}")
        return None

def main():
    for root, dirs, files in os.walk("."):
        # Filtrer les dossiers ignorés
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                # On évite de traduire les fichiers déjà traduits
                if file.startswith("fr_"):
                    continue
                
                file_path = os.path.join(root, file)
                print(f"Traduction de : {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_text = f.read()
                
                translated_text = translate_content(original_text, file)
                
                if translated_text:
                    # On crée un nouveau fichier préfixé par 'fr_'
                    new_path = os.path.join(root, f"fr_{file}")
                    with open(new_path, 'w', encoding='utf-8') as f:
                        f.write(translated_text)

if __name__ == "__main__":
    main()
