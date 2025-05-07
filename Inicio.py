
import streamlit as st

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="Kiosco App - Login",
    page_icon="🛒",
    layout="centered" # "wide" or "centered"
)

# --- Main Application ---
st.title("One Drop")


# Check if the user is already logged in (using session state)
if not st.session_state.get("logged_in", False):
    # If not logged in, show the login form
    with st.form("login_form"):
        username = st.text_input("Username (any value)")
        password = st.text_input("Password (any value)", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # For this demo, any username/password is accepted
            if username and password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username # Optional: store username
                st.success("Login successful!")
            else:
                st.error("Please enter both username and password.")
else:
    # If logged in, show a welcome message
    st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
    st.info("Navigate using the sidebar on the left to manage different sections.")
    #st.balloons() # Fun little animation

    # Optional: Add a logout button
    if st.button("Logout"):
        del st.session_state["logged_in"]
        if "username" in st.session_state:
            del st.session_state["username"]