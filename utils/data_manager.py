import fsspec, posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    A singleton class for managing application data persistence and user-specific storage.
    This class provides a centralized interface for handling both application-wide and
    user-specific data storage operations. It implements a singleton pattern using
    Streamlit's session state to maintain consistency across app reruns.
    Key Features:
        - Singleton implementation for consistent state management
        - Flexible filesystem support (local and WebDAV)
        - Separate handling of application and user-specific data
        - Integration with Streamlit's session state
        - Automatic data persistence
        >>> data_manager = DataManager()
        >>> data_manager.load_app_data("settings", "settings.json", initial_value={})
        >>> data_manager.load_user_data("user_prefs.json", initial_value={})
        >>> data_manager.save_all_data()

    Attributes:
        fs (fsspec.AbstractFileSystem): The filesystem interface for data storage
        fs_root_folder (str): Root directory for all file operations
        app_data_reg (dict): Registry of application-wide data files
        user_data_reg (dict): Registry of user-specific data files
        - Uses fsspec for filesystem operations
        - Requires Streamlit session state for persistence
        - Automatically manages user data separation
        - Implements data registry for tracking stored files
    """

    def __new__(cls, *args, **kwargs):
        """
        Implements singleton pattern by returning existing instance from session state if available.

        Returns:
            AppManager: The singleton instance, either existing or newly created
        """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance
    
    def __init__(self, fs_protocol = 'file', fs_root_folder = 'app_data'):
        """
        Initialize the data manager with filesystem configuration.
        Sets up the filesystem interface and initializes data registries for the application.
        If the instance is already initialized (has 'fs' attribute), the initialization is skipped.
            fs_protocol (str, optional): Protocol to use for filesystem operations.
                Can be 'file' or 'webdav'. Defaults to 'file'.
            fs_root_folder (str, optional): Base directory path for all file operations.
                Defaults to 'app_data'.
        Attributes:
            fs_root_folder (str): Base directory path for file operations
            fs: Filesystem interface instance
            app_data_reg (dict): Registry for application-wide data
            user_data_reg (dict): Registry for user-specific data
        """
        if hasattr(self, 'fs'):  # check if instance is already initialized
            return
            
        # initialize filesystem stuff
        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    @staticmethod
    def _init_filesystem(protocol: str):
        """
        Creates and configures an fsspec filesystem instance.

        Supports WebDAV protocol using credentials from Streamlit secrets, and local filesystem access.
        
        Args:
            protocol: The filesystem protocol to initialize ('webdav' or 'file')
            
        Returns:
            fsspec.AbstractFileSystem: Configured filesystem instance
            
        Raises:
            ValueError: If an unsupported protocol is specified
        """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav', 
                                     base_url=secrets['base_url'], 
                                     auth=(secrets['username'], secrets['password']))
        elif protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"AppManager: Invalid filesystem protocol: {protocol}")

    def _get_data_handler(self, subfolder: str = None):
        """
        Creates a DataHandler instance for the specified subfolder.

        Args:
            subfolder: Optional subfolder path relative to root folder

        Returns:
            DataHandler: Configured for operations in the specified folder
        """
        if subfolder is None:
            return DataHandler(self.fs, self.fs_root_folder)
        else:
            return DataHandler(self.fs, posixpath.join(self.fs_root_folder, subfolder))

    def load_app_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Load application data from a file and store it in the Streamlit session state.

        Args:
            session_state_key (str): Key under which the data will be stored in Streamlit's session state
            file_name (str): Name of the file to load data from
            initial_value (Any, optional): Default value if file doesn't exist. Defaults to None.
            **load_args: Additional keyword arguments to pass to the data handler's load method

        Returns:
            None: The loaded data is stored directly in Streamlit's session state

        Note:
            The method also registers the file name in the app_data_reg dictionary using the session_state_key
        """
        if session_state_key in st.session_state:
            return
        
        dh = self._get_data_handler()
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.app_data_reg[session_state_key] = file_name

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Load user-specific data from a file in the user's data folder.

        Args:
            session_state_key (str): Key under which the data will be stored in Streamlit's session state
            file_name (str): Name of the file to load data from
            initial_value: Default value to return if file doesn't exist (default: None)
            **load_args: Additional arguments to pass to the data handler's load method

        Returns:
            The loaded data from the file

        Raises:
            ValueError: If no user is currently logged in

        Notes:
            - The method registers the file name in the user_data_reg dictionary
            - The user's data folder is named 'user_data_<username>'
            - If no user is logged in, all user data is cleared from session state
        """
        username = st.session_state.get('username', None)
        if username is None:
            for key in self.user_data_reg:  # delete all user data
                st.session_state.pop(key)
            self.user_data_reg = {}
            st.error(f"DataManager: No user logged in, cannot load file `{file_name}` into session state with key `{session_state_key}`")
            return
        elif session_state_key in st.session_state:
            return

        user_data_folder = 'user_data_' + username

        dh = self._get_data_handler(user_data_folder)
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = dh.join(user_data_folder, file_name)

    @property
    def data_reg(self):
        return {**self.app_data_reg, **self.user_data_reg}

    def save_data(self, session_state_key):
        """
        Saves data from session state to persistent storage using the registered data handler.

        Args:
            session_state_key (str): Key identifying the data in both session state and data registry

        Raises:
            ValueError: If the session_state_key is not registered in data_reg
            ValueError: If the session_state_key is not found in session state

        Example:
            >>> data_manager.save_data("user_settings")
        """
        if session_state_key not in self.data_reg:
            raise ValueError(f"DataManager: No data registered for session state key {session_state_key}")
        
        if session_state_key not in st.session_state:
            raise ValueError(f"DataManager: Key {session_state_key} not found in session state")
        
        dh = self._get_data_handler()
        dh.save(self.data_reg[session_state_key], st.session_state[session_state_key])

    def save_all_data(self):
        """
        Saves all valid data from the session state to the persistent storage.

        This method iterates through all registered data keys and saves the corresponding 
        data if it exists in the current session state.

        Uses the save_data() method internally for each individual key.
        """
        keys = [key for key in st.data_reg.key() if key in self.session_state]
        for key in keys:
            self.save_data(key)


    def append_record(self,session_state_key, record_dict):
        """
        Append a new record to a value stored in the session state. The value must be either a list or a DataFrame.

        Args:
            session_state_key (str): Key identifying the value in the session state
            record_dict (dict): Dictionary containing the new record to append

        Raises:
            ValueError: If the session_state_key is not found in session state
            ValueError: If the session state value is not a list or a DataFrame
            ValueError: If the record_dict is not a dictionary

        Returns:
            None: The updated value is stored back in the session state

        """
        data_value = st.session_state[session_state_key]
        
        if not isinstance(record_dict, dict):
            raise ValueError(f"DataManager: The record_dict must be a dictionary")
        
        if isinstance(data_value, pd.DataFrame):
            data_value = pd.concat([data_value, pd.DataFrame([record_dict])], ignore_index=True)
        elif isinstance(data_value, list):
            data_value.append(record_dict)
        else:
            raise ValueError(f"DataManager: The session state value for key {session_state_key} must be a DataFrame or a list")
        
        st.session_state[session_state_key] = data_value
        self.save_data(session_state_key)