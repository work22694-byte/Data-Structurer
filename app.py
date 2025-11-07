import streamlit as st
from Data_Structure import data_structurer  # <-- your file name here

st.markdown(
    "<h1 style='text-align: center;'> Data Structurer</h1>",
    unsafe_allow_html=True
)


instruction = st.text_input("Instruction", "Clean and structure this data into a table")
columns = st.number_input("Expected number of columns", min_value=1, value=3)
data = st.text_area("Paste your messy data below:", height=200)

if st.button("Run"):
    if not data.strip():
        st.warning("⚠️ Please paste some data first.")
    else:
        with st.spinner(" Cleaning your data..."):
            result = data_structurer(instruction, data, columns)

            if "error" in result:
                st.error(result["error"])
                st.text_area("Raw Output", result["raw_output"], height=200)
            else:
                df = result["dataframe"]
                summary = result["summary"]

                st.success("Process successfully Completed!")
                st.dataframe(df, use_container_width=True)

                st.subheader(" Data Summary")
                st.json(summary)
