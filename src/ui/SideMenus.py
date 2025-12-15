# SideMenus.py
import streamlit as st

from ui.ApiKey import ApiKey
from ui.ClientController import ClientController
from ui.UserInputs import UserInputs


class SideMenus:
    def __init__(self):
        # インスタンス化
        self.api_key_component = ApiKey()
        self.client_controller = ClientController()
        self.user_inputs_component = UserInputs()

    def render_api_client_menu(self):
        with st.sidebar:
            self.api_key_component.input_key()
            self.user_inputs_component.render_dynamic_inputs()
            self.user_inputs_component.render_property_path()
            with st.expander("session_state", expanded=False):
                st.write(st.session_state)
            self.client_controller.render_buttons()

    def set_user_property_path(self, response_path):
        # st.session_state.user_property_path = response_path
        self.user_inputs_component.set_user_property_path(response_path)
