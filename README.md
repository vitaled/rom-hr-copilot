# HR Copilot

## Description

## Run locally

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

## Run on Azure

### Using Azure Development CLI

#### Prerequisites

1. Install the Azure Development CLI following the instructions [here](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=winget-windows%2Cbrew-mac%2Cscript-linux&pivots=os-windows)

2. Install Git following the instructions [here](https://git-scm.com/downloads)

3. Install Docker Desktop following the instructions [here](https://www.docker.com/products/docker-desktop)

#### Deploying the application

Clone this repository:

```ps1
git clone https://github.com/vitaled/rom-hr-copilot
```

Navigate to the code directory

```ps1
cd code
```

Login to Azure using azd:

```ps1
azd auth login
```

Create the infrastructure and deploy the application:

```ps1
azd up
```
