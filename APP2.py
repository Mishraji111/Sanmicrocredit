import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- APP CONFIGURATION ---
st.set_page_config(page_title="MicroFin Track", layout="wide")

# --- CUSTOM CSS FOR MOBILE LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .card { padding: 15px; border-radius: 10px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA (Simulating your Excel Sheet) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Staff': ['Nandlal', 'Dhiraj', 'Nandlal'],
        'Centre': ['Salarpur', 'Ashapur', 'Sandaha'],
        'Client': ['Kiran', 'Basanti', 'Meena'],
        'Loan_Amount': [12000, 6000, 12000],
        'Paid_So_Far': [2400, 1200, 0],
        'Last_Day_Paid': [12, 6, 0]
    })

# --- APP NAVIGATION ---
menu = ["Dashboard", "Collection", "Add Client", "Reports"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- DASHBOARD ---
if choice == "Dashboard":
    st.title("Field Officer Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Target", "₹24,000")
    with col2:
        st.metric("Collected Today", "₹4,200", delta="18%")
    
    st.subheader("Your Schedule Today")
    for centre in st.session_state.data['Centre'].unique():
        with st.expander(f"📍 Centre: {centre}"):
            st.write(f"Clients pending: {len(st.session_state.data[st.session_state.data['Centre']==centre])}")
            if st.button(f"Start {centre} Meeting"):
                st.session_state.active_centre = centre

# --- COLLECTION MODULE (The Excel Replacement) ---
elif choice == "Collection":
    st.title("Daily Collection Ledger")
    staff_filter = st.selectbox("Select Staff", ["Nandlal", "Dhiraj"])
    centre_filter = st.selectbox("Select Centre", st.session_state.data['Centre'].unique())
    
    clients = st.session_state.data[
        (st.session_state.data['Staff'] == staff_filter) & 
        (st.session_state.data['Centre'] == centre_filter)
    ]
    
    for index, row in clients.iterrows():
        st.markdown(f"""
        <div class="card">
            <strong>Client: {row['Client']}</strong><br>
            Loan: ₹{row['Loan_Amount']} | Day: {row['Last_Day_Paid']}/60<br>
            Expected Today: ₹200
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button(f"Mark Paid (₹200)", key=f"pay_{index}"):
            st.success(f"Collected from {row['Client']}")
        if c2.button(f"No Payment", key=f"miss_{index}"):
            st.warning("Marked as Missed")

# --- REPORTS ---
elif choice == "Reports":
    st.title("Pivot Summary")
    st.write("Current Loan Status by Centre")
    pivot = st.session_state.data.pivot_table(index='Centre', values='Loan_Amount', aggfunc='sum')
    st.bar_chart(pivot)
    st.table(st.session_state.data)
    import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Sandaha Microfinance", layout="wide")

# File name must match exactly what you uploaded to GitHub
EXCEL_FILE = "Backup file Sandaha detail.xlsx"

@st.cache_data
def load_data():
    try:
        # We load Sheet1 as per your file structure
        df = pd.read_excel(EXCEL_FILE, sheet_name="Sheet1")
        # Clean up column names (remove hidden spaces)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error(f"⚠️ Error: Could not find '{EXCEL_FILE}' in your GitHub repository.")
    st.info("Please make sure you uploaded the Excel file to the same folder as app.py on GitHub.")
else:
    st.title("💸 Sandaha Collection App")
    
    # Sidebar Filters
    st.sidebar.header("Filter")
    staff_member = st.sidebar.selectbox("Select Staff", df['Staff'].dropna().unique())
    centre_name = st.sidebar.selectbox("Select Centre", df[df['Staff'] == staff_member]['Centre'].dropna().unique())

    # Filtered Data
    mask = (df['Staff'] == staff_member) & (df['Centre'] == centre_name)
    active_clients = df[mask]

    st.subheader(f"Clients for {staff_member} at {centre_name}")

    # Displaying Clients in a Mobile-Friendly way
    for index, row in active_clients.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{row['Client Name']}** (Husband: {row['Husband']})")
                st.caption(f"Loan: ₹{row['Loan Amount']} | Due: ₹{row['Amount Due']}")
            
            with col2:
                # This identifies which 'Day' column to update based on your Excel's 'Pending Period Days'
                current_day = int(row['Pending Period Days']) if pd.notnull(row['Pending Period Days']) else 1
                if st.button(f"Collect Day {current_day}", key=f"btn_{index}"):
                    st.success(f"Collected for {row['Client Name']}")

    # Dashboard/Analytics Section
    st.divider()
    st.subheader("📊 Centre Summary")
    total_disbursed = active_clients['Loan Amount'].sum()
    total_due = active_clients['Amount Due'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Disbursed", f"₹{total_disbursed:,}")
    c2.metric("Pending Balance", f"₹{total_due:,}")