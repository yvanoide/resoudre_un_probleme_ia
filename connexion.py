import streamlit as st
from streamlit_chat import message
import requests

# Définir les URLs directement ici
URL_VERSIONS = "http://127.0.0.1:8080/versions"
URL_TRADUCTEUR = "http://127.0.0.1:8080/traductions"
URL_TRADUCTIONS = "http://127.0.0.1:8080/traductions/auteur/"
URL_LOGIN = "http://127.0.0.1:8080/login"

class TraducteurApp:
    def __init__(self):
        self.URL_TRADUCTEUR = URL_TRADUCTEUR
        self.URL_VERSIONS = URL_VERSIONS
        self.URL_LOGIN = URL_LOGIN
        self.URL_TRADUCTIONS = URL_TRADUCTIONS
        self.titre = "Traducteur"

        st.set_page_config(
            page_title="Traducteur",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = None

        if st.session_state["logged_in"]:
            self.show_app()
        else:
            self.show_login_form()

    def show_login_form(self):
        def login(username, password):
            data = {
                "login": username,
                "mdp": password
            }

            response = requests.post(self.URL_LOGIN, json=data)

            if response.status_code == 200:
                response_login = response.json()

                if response_login.get("authentifié"):
                    st.session_state["logged_in"] = response_login["id"]
                    st.experimental_rerun()  # Recharger l'application pour afficher la vue du traducteur
                else:
                    st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect")
            else:
                st.sidebar.error(f"Erreur lors de la connexion : {response.status_code} - {response.text}")

        st.sidebar.title("Connexion")
        username = st.sidebar.text_input("Nom d'utilisateur")
        password = st.sidebar.text_input("Mot de passe", type="password")
        st.sidebar.button("Se connecter", on_click=login, args=(username, password))

    def show_index(self):
        st.title(self.titre)
        st.write("Veuillez vous connecter pour accéder aux fonctionnalités sécurisées.")
        
    def show_logout_button(self):
        def logout():
            st.session_state["logged_in"] = None
            st.experimental_rerun()  # Recharger l'application après déconnexion
    
        st.sidebar.title("Déconnexion")
        st.sidebar.button("Se déconnecter", on_click=logout)

    def show_app(self):
        st.title(self.titre)
        self.show_logout_button()
        st.write(f"Utilisateur connecté avec ID: {st.session_state['logged_in']}")
        
        versions = self.get_versions()
        st.write(f"Versions disponibles: {versions}")

        option = st.sidebar.selectbox(
            "Choisissez la traduction à réaliser :",
            versions
        )

        self.add_form(option)
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
            data = {
                "atraduire": atraduire,
                "version": option,
                "utilisateur": st.session_state["logged_in"]
            }

            response = requests.post(self.URL_TRADUCTEUR, json=data)

            if response.status_code == 200:
                st.success("Voici votre traduction !")
                response_data = response.json()
                reponse = f"{response_data['traduction'][0]['translation_text']}"
                st.write(reponse)
            else:
                st.error(f"Erreur : {response.status_code}")
                st.json(response.json())

    def add_chat(self):
        url = f"{self.URL_TRADUCTIONS}{st.session_state.logged_in}"
        chat = requests.get(url)

        if chat.status_code == 200:
            chat_messages = chat.json()

            for prompt in chat_messages:
                message(prompt["atraduire"], is_user=True)
                message(prompt["traduction"])
        else:
            st.error(f"Erreur : {chat.status_code}")

# Initialisation de l'application
TraducteurApp()
