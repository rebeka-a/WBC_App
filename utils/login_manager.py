import secrets
import re
import time
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton class that manages application state, storage, and user authentication.
    """

    def __new__(cls, *args, **kwargs):
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance

    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        if hasattr(self, 'authenticator'):
            return

        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Register new user'):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            login_tab, register_tab = st.tabs((login_title, register_title))
            with login_tab:
                self.login(stop=False)
            with register_tab:
                self.register()

    def login(self, stop=True):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("Username/Passwort ist falsch.")
            else:
                st.warning("Bitte Benutzername und Passwort eingeben.")
            if stop:
                st.stop()

    def register(self, stop=True):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            Das Passwort muss 8–20 Zeichen lang sein und mindestens einen Großbuchstaben, 
            einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen @$!%*?& enthalten.
            """)

            with st.form("Registrierungsformular"):
                email = st.text_input("E-Mail")
                username = st.text_input("Benutzername")
                first_name = st.text_input("Vorname")
                last_name = st.text_input("Nachname")
                password = st.text_input("Passwort", type="password")
                submit = st.form_submit_button("Registrieren")

            if submit:
                with st.spinner("⏳ Registrierung wird verarbeitet..."):
                    time.sleep(1)  # rein visuell

                    # E-Mail validieren
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        st.error("Bitte gib eine gültige E-Mail-Adresse ein.")
                        return

                    if not all([email, username, first_name, last_name, password]):
                        st.error("Bitte fülle alle Felder aus.")
                        return

                    # Passwortanforderungen prüfen (kann erweitert werden)
                    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,20}$', password):
                        st.error("Passwort erfüllt nicht die Anforderungen.")
                        return

                    try:
                        res = self.authenticator.register_user(
                            first_name, last_name, username, email, password
                        )
                        if res[1] is not None:
                            st.success(f"Nutzer *{res[1]}* wurde erfolgreich registriert.")
                            self._save_auth_credentials()
                            st.success("Zugangsdaten wurden gespeichert.")
                        else:
                            st.error("Registrierung fehlgeschlagen. Möglicherweise existiert der Benutzer bereits.")
                    except Exception as e:
                        st.error(f"Registrierung nicht möglich: {str(e)}")

            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Wenn der Nutzer nicht eingeloggt ist, zur Login-Seite weiterleiten.
        Zeigt beim Warten eine schöne Ladeanimation.
        """
        if st.session_state.get("authentication_status") is None:
            # Ladeanimation anzeigen
            st.markdown(
                """
                <style>
                .centered-loader {
                    position: fixed;
                    top: 40%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 1.8rem;
                    font-weight: 600;
                    color: #444;
                    animation: pulse 1.8s infinite;
                }

                @keyframes pulse {
                    0%   { opacity: 0.2; }
                    50%  { opacity: 1; }
                    100% { opacity: 0.2; }
                }
                </style>

                <div class="centered-loader">⏳ Bitte warten...</div>
                """,
                unsafe_allow_html=True
            )
            st.stop()

        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()
