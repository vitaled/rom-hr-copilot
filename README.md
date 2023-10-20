# HR Copilot

## Description

## How to run

### Prerequisites

### Standalone

Create a virtual environment

```ps1
virtualenv venv
```

Activate the virtual environment

```ps1
.env\Scripts\activate
```

Move to the code directory

```ps1
cd code
```

Install the dependencies

```ps1
pip install -r requirements.txt
```

Create environment variables file `.env` and set the following variables

```text
API_TYPE=azure
API_VERSION=2023-03-15-preview
API_BASE=<OPEN AI SERVICE ENDPOINT>
API_KEY=<OPEN AI SERVICE KEY>
OPENAI_ENGINE=<model deployment name>
OPENAI_MAX_TOKENS=<max number of tokens for model>
FORM_RECOGNIZER_ENDPOINT=<FORM_RECOGNIZER_ENDPOINT>
FORM_RECOGNIZER_KEY=<FORM RECOGNIZER KEY>
```

Run the application

```ps1
streamlit run Home.py --server.port 80 --server.enableXsrfProtection false
```
