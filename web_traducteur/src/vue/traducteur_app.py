import streamlit as st
from streamlit_chat import message
from config.parametres import URL_TRADUCTEUR, URL_VERSIONS, URL_LOGIN, URL_TRADUCTIONS
import requests
from transformers import pipeline
from prometheus_client import start_http_server, Counter, Histogram, Gauge, REGISTRY
import time

class TraducteurApp:
    def __init__(self):
        self.URL_TRADUCTEUR = URL_TRADUCTEUR
        self.URL_VERSIONS = URL_VERSIONS
        self.URL_LOGIN = URL_LOGIN
        self.URL_TRADUCTIONS = URL_TRADUCTIONS
        self.titre = "Traducteur"

        # Initialisation du pipeline de traduction
        self.translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

        # Initialisation des métriques Prometheus
        if 'translation_requests_total' not in REGISTRY._names_to_collectors:
            self.translation_counter = Counter('translation_requests_total', 'Total number of translation requests')
        else:
            self.translation_counter = REGISTRY._names_to_collectors['translation_requests_total']

        if 'response_time_seconds' not in REGISTRY._names_to_collectors:
            self.response_time = Histogram('response_time_seconds', 'Response time in seconds')
        else:
            self.response_time = REGISTRY._names_to_collectors['response_time_seconds']

        if 'response_length_chars' not in REGISTRY._names_to_collectors:
            self.response_length = Gauge('response_length_chars', 'Length of the response in characters')
        else:
            self.response_length = REGISTRY._names_to_collectors['response_length_chars']

        st.set_page_config(
            page_title="Traducteur",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = None

        self.show_login_form()

        if st.session_state["logged_in"]:
            self.show_app()
        else:
            self.show_index()

    def show_login_form(self):
        # Identifiants prédéfinis
        valid_username = "Cleese"
        valid_password = "Sacré Graal!"

        def login(username, password):
            # Vérifier les identifiants
            if username == valid_username and password == valid_password:
                st.session_state["logged_in"] = True
            else:
                st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect")

        st.sidebar.title("Connexion")
        username = st.sidebar.text_input("Nom d'utilisateur")
        password = st.sidebar.text_input("Mot de passe", type="password")
        st.sidebar.button("Se connecter", on_click=login, args=(username, password))

    def show_index(self):
        st.title(self.titre)
        st.write("Bienvenue dans l'application Traducteur!")
        st.write("Veuillez vous connecter pour accéder aux fonctionnalités sécurisées.")

    def show_app(self):
        st.title(self.titre)
        versions = self.get_versions()

        option = st.sidebar.selectbox(
            "Choisissez la traduction à réaliser :",
            versions
        )

        self.add_form(option)

        if st.session_state["logged_in"]:
            self.add_chat()

    def get_versions(self):
        versions = ["Aucune langue détectée !"]
        response = requests.get(self.URL_VERSIONS)

        if response.status_code == 200:
            versions = response.json()
        else:
            st.error(f"Erreur : {response.status_code}")
        return versions

    def add_form(self, option):
        st.subheader(option)
        atraduire = st.text_input("Texte à traduire")

        if st.button("Traduire"):
            start_time = time.time()

            # Incrémenter le compteur de traductions
            self.translation_counter.inc()

            # Utilisation du pipeline de traduction
            phrase_traduite = self.translator(atraduire, max_length=40)[0]['translation_text']
            st.success("Voici votre traduction !")
            st.write(phrase_traduite)

            # Mesurer le temps de réponse
            response_time = time.time() - start_time
            self.response_time.observe(response_time)

            # Mesurer la longueur de la réponse
            self.response_length.set(len(phrase_traduite))

    def add_chat(self):
        url = f"{self.URL_TRADUCTIONS}{st.session_state['logged_in']}"
        chat = requests.get(url)

        if chat.status_code == 200:
            chat_messages = chat.json()

            for prompt in chat_messages:
                message(prompt["atraduire"], is_user=True)
                message(prompt["traduction"])

if __name__ == "__main__":
    # Démarrer le serveur Prometheus sur le port 8501
    start_http_server(8501)
    TraducteurApp()
