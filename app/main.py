import streamlit as st
from interface import WeaviateInterface

def main():
    st.title("Weaviate Vector Database Manager")

    weaviate_interface = WeaviateInterface()

    if weaviate_interface.check_connection():
        st.success("Connected to Weaviate!")
        
        collections = weaviate_interface.get_collection_names()
        selected_collection = st.selectbox("Select a collection", collections)

        if st.button("View Contents"):
            contents = weaviate_interface.view_contents_of_collection(selected_collection)
            if contents:
                st.write(contents)
            else:
                st.write("No contents found in the selected collection.")
    else:
        st.error("Failed to connect to Weaviate.")

if __name__ == "__main__":
    main()