import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton class that manages application state, storage, and user authentication.
    
    Handles filesystem access, user credentials, and authentication state using Streamlit's
    session state for persistence across reruns. Provides interfaces for accessing user-specific
    and application-wide data storage.
    """
    def __new__(cls, *args, **kwargs):
        """
        Implements singleton pattern by returning existing instance from session state if available.

        Returns:
            AppManager: The singleton instance, either existing or newly created
        """
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance
    
    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        """
        Initializes filesystem and authentication components if not already initialized.

        Sets up filesystem access using the specified protocol and configures authentication
        with cookie-based session management.

        Args:
            Data_manager: The DataManager instance to use for data storage
            auth_credentials_file (str): The filename to use for storing user credentials
            auth_cookie_name (str): The name of the cookie to use for session management
        """
        if hasattr(self, 'authenticator'):  # check if instance is already initialized
            return
        
        if data_manager is None:
            return

        # initialize streamlit authentication stuff
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)


    def _load_auth_credentials(self):
        """
        Loads user credentials from the configured credentials file.

        Returns:
            dict: User credentials, defaulting to empty usernames dict if file not found
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value= {"usernames": {}})

    def _save_auth_credentials(self):
        """
        Saves current user credentials to the credentials file.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title = 'Login', register_title = 'Register new user'):
        """
        Renders the authentication interface.
        
        Displays login form and optional registration form. Handles user authentication
        and registration flows. Stops further execution after rendering.
        
        Args:
            show_register_tab: If True, shows registration option alongside login
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            login_tab, register_tab = st.tabs((login_title, register_title))
            with login_tab:
                self.login(stop=False)
            with register_tab:
                self.register()

    def login(self, stop=True):
        """
        Renders the login form and handles authentication status messages.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("Username/password is incorrect")
            else:
                st.warning("Please enter your username and password")
            if stop:
                st.stop()

    def register(self,stop=True):
        """
        Renders the registration form and handles user registration flow.
        
        Displays password requirements, processes registration attempts,
        and saves credentials on successful registration.
        """

        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            The password must be 8-20 characters long and include at least one uppercase letter, 
            one lowercase letter, one digit, and one special character from @$!%*?&.
            """)
            res = self.authenticator.register_user()
            if res[1] is not None:
                st.success(f"User {res[1]} registered successfully")
                try:
                    self._save_auth_credentials()
                    st.success("Credentials saved successfully")
                except Exception as e:
                    st.error(f"Failed to save credentials: {e}")
            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Create a logout button that logs the user out and redirects to the login page.
        If the user is not logged in, the login page is displayed.

        Parameters
        - login_page_py_file (str): The path to the Python file that contains the login page
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout() # create logout button