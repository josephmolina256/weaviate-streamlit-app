import streamlit as st
from interface import WeaviateInterface
import warnings

import json

from constants import SLACK_WORKSPACE_NAME


warnings.simplefilter("ignore", ResourceWarning)

def main():
    st.title("Weaviate Vector Database Manager")

    weaviate_interface = WeaviateInterface()

    if "edit_states" not in st.session_state:
        st.session_state.edit_states = {}

    if weaviate_interface.check_connection():
        st.success("Connected to Weaviate!")
        
        collections = weaviate_interface.get_collection_names()
        selected_collection = st.selectbox("Select a collection", collections)

       
        if st.button("Refresh Contents"):
            st.session_state.contents = weaviate_interface.view_contents_of_collection(selected_collection)
        

        if "contents" in st.session_state:
            if st.session_state.contents:
                for i, item in enumerate(st.session_state.contents):
                    st.write(item)

                    col1, col2, col3 = st.columns([0.2, 0.2,  0.6])

                    with col1:
                        if st.button(f"Edit Item", key=f"edit-btn-{i}"):
                            st.session_state.edit_states[item["uuid"]] = True

                    with col2:
                        if st.button(f"Delete Item", key=f"delete-{i}"):
                            weaviate_interface.delete_item(selected_collection, item["uuid"], item["thread_ts"])
                            st.session_state.contents.pop(i)
                    with col3:
                        st.link_button(label="View in Slack", url=f"https://{SLACK_WORKSPACE_NAME}.slack.com/archives/{item['channel_id']}/p{item['thread_ts'].replace('.', '')}?thread_ts={item['thread_ts']}&cid={item['channel_id']}")

                    if st.session_state.edit_states.get(item["uuid"], False):
                        text_value = item.get("responses", None)
                        text_label = "responses"
                        if not text_value:
                            text_value = item.get("head", None)
                            text_label = "head"

                        updated_text = st.text_area(f'Edit the Item\'s "{text_label}" Field Below:', value=text_value, key=f"text-{i}", height=200)

                        col1, col2, col3 = st.columns([1, 1, 2])

                        with col1:
                            if st.button(f"Submit Edits", key=f"submit-{i}"):
                                updated_item = weaviate_interface.update_item(
                                    collections_name=selected_collection,
                                    item=item, 
                                    updated_text=updated_text, 
                                    key_to_be_updated=text_label)
                                st.write(f"Item updated: {updated_item}")
                                st.session_state.edit_states[item["uuid"]] = False

                        with col2:
                            if st.button(f"Cancel Edits", key=f"cancel-edits-{i}"):
                                st.write(f"Item Update Cancelled")
                                st.session_state.edit_states[item["uuid"]] = False

                        
                        

            else:
                st.write("No contents found in the selected collection.")
    else:
        st.error("Failed to connect to Weaviate.")

if __name__ == "__main__":
    main()
