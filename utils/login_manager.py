import secrets
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import RegisterError
from utils.data_manager import DataManager


class LoginManager:
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
                    "registration_successful": "Registrierung erfolgreich.",
                    "user_exists": "Benutzername oder E-Mail existiert bereits.",
                    "captcha": "Sicherheitsfrage: Wie viel ist 3 + 4?"
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

    def login_register(self, login_title='Anmeldung', register_title='Registrierung'):
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
            Das Passwort muss 8 – 20 Zeichen lang sein und mindestens einen Großbuchstaben, 
            einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen @$!%*?& enthalten.
            """)
            try:
                res = self.authenticator.register_user()
                if res[1] is not None:
                    st.success(f"Nutzer *{res[1]}* wurde erfolgreich registriert.")
                    try:
                        self._save_auth_credentials()
                        st.success("Zugangsdaten wurden gespeichert.")
                    except Exception:
                        st.error("Fehler beim Speichern der Zugangsdaten.")
            except RegisterError:
                st.error("Registrierung fehlgeschlagen. Bitte überprüfe deine Eingaben.")

            if stop:
                st.stop()

    def go_to_login(self, login_page_title: str):
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_title)
        else:
            self.authenticator.logout()
