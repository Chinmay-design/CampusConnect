import streamlit as st
from database import load_data, save_data, get_user_by_id

def profile_page():
    # Check if viewing another user's profile
    if st.session_state.get('viewing_profile'):
        view_public_profile()
        return
    
    st.title("👤 My Profile")
    
    user = st.session_state.user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(user['name'])
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Year:** {user.get('year', 'Not set')}")
        st.write(f"**Branch:** {user.get('branch', 'Not set')}")
        st.write(f"**Role:** {user.get('role', 'student')}")
        
        # Display interests
        interests = user.get('interests', [])
        if interests:
            st.write("**My Interests:**")
            for interest in interests:
                st.write(f"• {interest}")
    
    with col2:
        # Activity stats
        clubs = load_data('clubs')
        user_clubs = sum(1 for club in clubs.values() if st.session_state.user['id'] in club.get('members', []))
        events = load_data('events')
        user_events = sum(1 for event in events.values() if st.session_state.user['id'] in event.get('rsvps', []))
        marketplace = load_data('marketplace')
        user_listings = sum(1 for item in marketplace.values() if item.get('seller_id') == st.session_state.user['id'])
        
        st.metric("Clubs Joined", user_clubs)
        st.metric("Events Attending", user_events)
        st.metric("Marketplace Listings", user_listings)
    
    # Edit profile
    with st.expander("✏️ Edit Profile"):
        with st.form("edit_profile"):
            new_name = st.text_input("Name", value=user['name'])
            new_year = st.selectbox("Year", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"], 
                                  index=["Freshman", "Sophomore", "Junior", "Senior", "Graduate"].index(user.get('year', 'Freshman')))
            new_branch = st.text_input("Branch", value=user.get('branch', ''))
            new_interests = st.text_area("Interests (comma-separated)", value=", ".join(user.get('interests', [])))
            
            if st.form_submit_button("Update Profile"):
                user['name'] = new_name
                user['year'] = new_year
                user['branch'] = new_branch
                user['interests'] = [interest.strip() for interest in new_interests.split(',') if interest.strip()]
                
                users = load_data('users')
                users[user['id']] = user
                save_data('users', users)
                
                st.session_state.user = user
                st.success("Profile updated!")
                st.rerun()

def view_public_profile():
    """View another user's public profile"""
    user_id = st.session_state.get('viewing_profile')
    user = get_user_by_id(user_id)
    
    if not user:
        st.error("User not found")
        if st.button("Back"):
            st.session_state.viewing_profile = None
            st.rerun()
        return
    
    st.title(f"👤 {user['name']}'s Profile")
    
    if st.button("⬅️ Back to Members"):
        st.session_state.viewing_profile = None
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.write(f"**Year:** {user.get('year', 'Not set')}")
        st.write(f"**Branch:** {user.get('branch', 'Not set')}")
        
        # Display interests
        interests = user.get('interests', [])
        if interests:
            st.write("**Interests:**")
            for interest in interests:
                st.write(f"• {interest}")
    
    with col2:
        # Public activity stats
        clubs = load_data('clubs')
        user_clubs = sum(1 for club in clubs.values() if user_id in club.get('members', []))
        events = load_data('events')
        user_events = sum(1 for event in events.values() if user_id in event.get('rsvps', []))
        
        st.metric("Clubs Joined", user_clubs)
        st.metric("Events Attending", user_events)
        
        # Action buttons
        if st.button("💬 Send Message", use_container_width=True):
            st.session_state.start_chat_with = user_id
            st.session_state.viewing_profile = None
            st.session_state.page = "Chat"
            st.rerun()
