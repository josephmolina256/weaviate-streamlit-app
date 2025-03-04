# Weaviate Streamlit App

This project is a Streamlit application that allows users to interact with a Weaviate vector database. Users can select a collection and view all items within that collection.

## Project Structure

```
weaviate-streamlit-app
├── app
│   ├── __init__.py
│   ├── interface.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd weaviate-streamlit-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command in your terminal:
```
streamlit run app/main.py
```

Once the application is running, you can select a collection from the dropdown menu and view all items in that collection.

## Dependencies

The project requires the following Python packages:

- Streamlit
- Weaviate client library
- Sentence Transformers (if applicable)

Make sure to install all dependencies listed in `requirements.txt`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.