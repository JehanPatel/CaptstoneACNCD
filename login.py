import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from email.message import EmailMessage
import smtplib
from st_pages import Page, show_pages, add_page_title
from streamlit_authenticator import Authenticate


st.set_page_config(page_title="Login", layout="wide")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

show_pages(
        [
            Page("C:\\Users\\91923\\Desktop\\Coding and Programming\\Capstone\\login.py","Login"),
            Page("C:\\Users\\91923\\Desktop\\Coding and Programming\\Capstone\\pages\\test.py","Code 1"),
            Page("C:\\Users\\91923\\Desktop\\Coding and Programming\\Capstone\\pages\\test1.py", "Code 2"),
            Page("C:\\Users\\91923\\Desktop\\Coding and Programming\\Capstone\\pages\\test2.py", "Code 3"),

        ]
    )

def load_config():
    with open('config.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

def is_bcrypt_hash(s):
    return s.startswith(('$2a$', '$2b$', '$2x$', '$2y$')) and len(s) == 60

# Hash new plaintext passwords only
def hash_plaintext_passwords(config):
    plaintext_passwords = {}
    for user, details in config['credentials']['usernames'].items():
        # Check if the password is not a bcrypt hash
        if not is_bcrypt_hash(details['password']):
            plaintext_passwords[user] = details['password']

    if plaintext_passwords:
        hashed_passwords = stauth.authenticate.Hasher(list(plaintext_passwords.values())).generate()
        for user, hashed_pw in zip(plaintext_passwords.keys(), hashed_passwords):
            config['credentials']['usernames'][user]['password'] = hashed_pw

    return config


# Save the config
def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


config = load_config()

if 'hashed_done' not in st.session_state:
    config = hash_plaintext_passwords(config)
    save_config(config)
    st.session_state.hashed_done = True

def st_authenticator():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
        file.close()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

    return authenticator

authenticator  = st_authenticator()
name, authentication_status, username = authenticator.login("Login","main")

if authentication_status:
    st.session_state.authentication_status = True
elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')
if authentication_status:
    # If the user is authenticated
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome to the app, *{name}*!')
    st.text('Click on any of the features on your left to get started!')