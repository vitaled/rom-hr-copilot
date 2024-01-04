import json
import pandas as pd
from dotenv import load_dotenv
from AzureCosmosDBClient import AzureCosmosDBClient
import uuid
from html.parser import HTMLParser


def read_candidate_info(file_path: str):
    """
    Read the candidate info from the file path
    """

    df = pd.read_csv(file_path, sep=";")

    df.fillna("", inplace=True)
    print([x.replace('&#039;', '\'') for x in df.columns])
    parser = HTMLParser()
    df.columns = [x.replace('&#039;', '\'') for x in df.columns]

    return df


def read_history(file_path: str):
    df = pd.read_excel(file_path)

    df.fillna("", inplace=True)
    print(df.columns)
    return df

def read_evaluations(file_path: str):
    df = pd.read_excel(file_path)

    df.fillna("", inplace=True)
    print(df.columns)
    return df

def main():
    load_dotenv()
    client = AzureCosmosDBClient()

    # candidates = read_candidate_info("../../data/HR Screening CV/ELENCO-CANDIDATI-403-972_utf8.csv")
    # client = AzureCosmosDBClient()

    # for row in candidates.iterrows():
    #     candidate = {}
    #     candidate["id"] = str(uuid.uuid4())

    #     for col in candidates.columns:
    #         candidate[col] = row[1][col]

    #     client.put_candidate(candidate)
    # history = read_history(
    #     "../../data/HR Screening CV/STORICO PARTECIPANT.XLS")
    # candidate = {}
    # for row in history.iterrows():
    #     if row[1]['Storico cod livello'] == 'LIVELLO ATTUALE':
    #         if candidate != {}:
    #             client.put_candidate(candidate)
    #         candidate = {}
    #         candidate["id"] = str(uuid.uuid4())
    #         candidate['CodiceFiscale'] = row[1]['CodiceFiscale']
    #         candidate['Matricola'] = row[1]['Matricola']
    #         candidate['Cognome'] = row[1]['Cognome']
    #         candidate['Nome'] = row[1]['Nome']
    #         candidate['Cod Reparto'] = row[1]['Cod Reparto']
    #         candidate['Reparto'] = row[1]['Reparto']
    #         candidate['Ex Cfl + varie'] = row[1]['Ex Cfl + varie']
    #         candidate['Posizione Giuridica attuale'] = row[1]['Posizione Giuridica attuale']
    #         candidate['Qualifica'] = row[1]['Qualifica']
    #         candidate['NConcorso'] = row[1]['NConcorso']
    #         candidate['Data assunzione'] = row[1]['Data assunzione'].strftime('%Y-%m-%d')
    #         candidate['Cod Livello attuale'] = row[1]['Cod Livello attuale']
    #         candidate['Storia Rapporto Lavorativo'] = []

    #     else:
            
    #         candidate['Storia Rapporto Lavorativo'].append({
    #             'Inizio rapp. lavorativo': row[1]['Inizio rapp. lavorativo'].strftime('%Y-%m-%d'),
    #             'Fine rapporto lavorativo': row[1]['Fine rapporto lavorativo'].strftime('%Y-%m-%d'),
    #             'Inizio inquadramento livello': row[1]['Inizio inquadramento livello'].strftime('%Y-%m-%d'),
    #             'Fine inquadramento livello': row[1]['Fine inquadramento livello'].strftime('%Y-%m-%d'),
    #             'Descrizione livello': row[1]['Descrizione livello']
    #         })
    #         print(candidate)
            
    evaluations = read_evaluations("../../data/HR Screening CV/PEV.xlsx")
    for row in evaluations.iterrows():
        candidates = list(client.get_candidate_by_cf(row[1]['CodiceFiscale']))
        if candidates != []:
            candidate = candidates[0]
            candidate["Matricola"] = row[1]['Matricola']
            candidate['III2020'] =  row[1]['III2020']
            candidate['IV2020'] = row[1]['IV2020']
            candidate['I2021'] = row[1]['I2021']
            candidate['II2021'] = row[1]['II2021']  
            candidate['I2022'] = row[1]['I2022']
            candidate['II2022'] = row[1]['II2022']
            candidate['I2023'] = row[1]['I2023']
            client.put_candidate(candidate)
main()
