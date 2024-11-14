import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Expense Splitter", page_icon="💸")

# Initialize session state to store expenses
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

# App title
st.title("Expense Splitting Calculator 💸")

# Sidebar for user input
st.sidebar.header("Add Participants")
participants = st.sidebar.text_input("Enter participant names, separated by commas (e.g., Alice, Bob, Charlie)")
if participants:
    participant_list = [name.strip() for name in participants.split(",")]
else:
    participant_list = []

# Expense entry section
st.header("Add a New Expense")
description = st.text_input("Description", placeholder="E.g., Dinner, Groceries")
amount = st.number_input("Amount", min_value=0.0, step=0.01)
payer = st.selectbox("Paid by", options=participant_list, help="Who paid for this expense?")
split_among = st.multiselect("Split among", options=participant_list, default=participant_list)

if st.button("Add Expense"):
    if description and amount > 0 and payer and split_among:
        expense = {
            "description": description,
            "amount": amount,
            "payer": payer,
            "split_among": split_among
        }
        st.session_state['expenses'].append(expense)
        st.success("Expense added!")
    else:
        st.error("Please complete all fields.")

# Display current expenses
st.header("Expense Summary")
if st.session_state['expenses']:
    # Convert expenses to DataFrame
    expense_df = pd.DataFrame(st.session_state['expenses'])
    st.write(expense_df)

    # Balance calculation
    balances = {person: 0 for person in participant_list}
    
    for expense in st.session_state['expenses']:
        amount_per_person = expense['amount'] / len(expense['split_among'])
        for person in expense['split_among']:
            if person == expense['payer']:
                balances[person] += expense['amount'] - amount_per_person
            else:
                balances[person] -= amount_per_person

    # Display balances
    st.subheader("Balance Summary")
    balance_df = pd.DataFrame(list(balances.items()), columns=["Participant", "Balance"])
    balance_df['Status'] = balance_df['Balance'].apply(lambda x: "Owes" if x < 0 else "Receives")
    st.write(balance_df)

    # Generate text summary
    summary = StringIO()
    summary.write("Expense Splitting Summary:\n\n")
    for person, balance in balances.items():
        if balance < 0:
            summary.write(f"{person} owes {abs(balance):.2f}\n")
        elif balance > 0:
            summary.write(f"{person} should receive {balance:.2f}\n")
        else:
            summary.write(f"{person} is settled up.\n")
    summary_content = summary.getvalue()
    summary.close()
    
    # Display and download summary as a text file
    st.subheader("Downloadable Summary")
    st.text(summary_content)
    st.download_button(
        label="Download Summary as Text File",
        data=summary_content,
        file_name="expense_summary.txt",
        mime="text/plain"
    )

else:
    st.info("No expenses added yet.")
