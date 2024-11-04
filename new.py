from transformers import pipeline

def traduire_phrase():
    # Initialisation du pipeline de traduction
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

    # Demander à l'utilisateur d'entrer une phrase en français
    phrase_fr = input("Entrez une phrase en français à traduire en anglais : ")

    # Traduire la phrase
    phrase_traduite = translator(phrase_fr, max_length=40)[0]['translation_text']

    # Afficher la phrase traduite
    print(f"Phrase traduite en anglais : {phrase_traduite}")

if __name__ == "__main__":
    traduire_phrase()
