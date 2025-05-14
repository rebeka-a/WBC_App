import secrets
import re
import time
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse zur Verwaltung von App-Zustand, Benutzerdaten und Authentifizierung.
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
            self.auth_cookie_key,
            cookie_expiry_days=30,
            translations={
                "login": {
                    "title": "Anmeldung",
                    "username": "Benutzername",
                    "password": "Passwort",
                    "login": "Einloggen",
                    "logout": "Abmelden",
                    "logged_in": "Eingeloggt als {name}.",
                    "login_failed": "Benutzername oder Passwort ist falsch.",
                    "login_required": "Bitte zuerst anmelden."
                },
                "register": {
                    "title": "Registrierung",
                    "first_name": "Vorname",
                    "last_name": "Nachname",
                    "email": "E-Mail",
                    "username": "Benutzername",
                    "password": "Passwort",
                    "register": "Registrieren",
                    "registration_successful": "Registrierung erfolgreich. Du kannst dich jetzt anmelden.",
                    "user_exists": "Benutzername oder E-Mail existiert bereits."
                },
                "reset_password": {
                    "title": "Passwort zurücksetzen",
                    "username": "Benutzername",
                    "new_password": "Neues Passwort",
                    "reset": "Zurücksetzen",
                    "password_reset_successful": "Passwort wurde erfolgreich zurückgesetzt."
                }
            }
        )

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Anmeldung', register_title='Registrieren'):
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
                st.error("Benutzername oder Passwort ist falsch.")
            else:
                st.warning("Bitte Benutzerdaten eingeben.")
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
                benutzername = st.text_input("Benutzername")
                vorname = st.text_input("Vorname")
                nachname = st.text_input("Nachname")
                passwort = st.text_input("Passwort", type="password")
                abschicken = st.form_submit_button("Registrieren")

            if abschicken:
                with st.spinner("⏳ Registrierung wird verarbeitet..."):
                    time.sleep(1)

                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        st.error("Bitte gib eine gültige E-Mail-Adresse ein.")
                        return

                    if not all([email, benutzername, vorname, nachname, passwort]):
                        st.error("Bitte fülle alle Felder aus.")
                        return

                    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,20}$', passwort):
                        st.error("Das Passwort erfüllt nicht die Anforderungen.")
                        return

                    try:
                        res = self.authenticator.register_user(
                            vorname, nachname, benutzername, email, passwort
                        )
                        if res[1] is not None:
                            st.success(f"Nutzer *{res[1]}* wurde erfolgreich registriert.")
                            self._save_auth_credentials()
                            st.success("Zugangsdaten wurden gespeichert.")
                        else:
                            st.error("Benutzername oder E-Mail existiert bereits.")
                    except Exception as e:
                        st.error(f"Registrierung fehlgeschlagen: {str(e)}")

            if stop:
                st.stop()

    def reset_password(self):
        """
        Passwort-Zurücksetzen-Formular.
        """
        st.subheader("🔒 Passwort zurücksetzen")
        try:
            username = st.text_input("Benutzername")
            new_password = st.text_input("Neues Passwort", type="password")
            if st.button("Zurücksetzen"):
                if not username or not new_password:
                    st.error("Bitte alle Felder ausfüllen.")
                    return
                result = self.authenticator.reset_password(username, new_password)
                if result:
                    self._save_auth_credentials()
                    st.success("Passwort wurde erfolgreich zurückgesetzt.")
                else:
                    st.error("Fehler beim Zurücksetzen. Benutzername nicht gefunden.")
        except Exception as e:
            st.error(f"Fehler: {str(e)}")

    def go_to_login(self, login_page_py_file):
        """
        Weiterleitung zur Login-Seite mit Ladeanimation, falls nicht eingeloggt.
        """
        if st.session_state.get("authentication_status") is None:
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
