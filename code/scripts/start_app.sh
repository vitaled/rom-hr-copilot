#!/bin/sh
python scripts/initCosmosDb.py;
streamlit run Home.py --server.port 8080 --server.enableXsrfProtection false;