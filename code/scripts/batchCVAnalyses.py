import os
import sys
base_path = os.getcwd()
print(base_path)
print(os.path.join(base_path, 'utilities'))
sys.path.insert(0, os.path.join(base_path))
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.AzureCosmosDBClient import AzureCosmosDBClient
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from utilities.LLMHelper import LLMHelper
import logging
from concurrent.futures import ProcessPoolExecutor
import uuid
import argparse
import traceback
import pandas as pd
import re
import json
from typing import List



def analyze(analysis_id, profile_id, resume_id, temperature, max_tokens):
    # create logger with 'spam_application'
    logname = os.path.join('./logs', 'analysis_' + analysis_id + '.log')
    logger = logging.getLogger('cv_analysis')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logname)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    try:

        cosmos_client = AzureCosmosDBClient()

        cosmos_client.set_analysis_run_running(analysis_id)

        analysis = None
        candidate = list(
            cosmos_client.get_candidates_by_resume_id(resume_id))[0]
        candidate_id = candidate["id"]
        analyses_query = cosmos_client.get_analysis_by_candidate_id_and_profile(
            candidate_id=candidate_id,
            profile_id=profile_id)

        analyses = list(analyses_query)
        cv_text = None
        total_score = 0
        if len(analyses) == 1:
            print("CV già analizzato... skipping")
            logger.info("CV già analizzato... skipping")
            cosmos_client.set_analysis_run_completed(analysis_id)
        else:
            print("CV non ancora analizzato")
            logger.info("CV non ancora analizzato")
            logger.info(f"Get profile: {profile_id}")
            prompts = list(cosmos_client.get_profile_by_id(profile_id))[
                0]['prompts']

            logger.info(f"Get Resume: {resume_id}")
            cv_text = list(cosmos_client.get_resume_by_id(resume_id))[
                0]['text']

            llm_helper = LLMHelper(
                temperature=temperature,
                max_tokens=max_tokens
            )

            for index, prompt in enumerate(prompts):
                prompt_text = prompt["text"]

                prompt_text = prompt_text.replace('{cv}', cv_text)

                history_table = candidate['Storia Rapporto Lavorativo']

                history_table = pd.DataFrame(history_table)
                history_table = history_table.to_markdown()
                prompt_text = prompt_text.replace('{storia_professionale}',
                                                  history_table)
                evaluation_table = candidate['Valutazioni']
                evaluation_table = pd.DataFrame(evaluation_table, index=[0])

                # Reset the index
                evaluation_table = evaluation_table.reset_index()
                # Use melt to pivot the DataFrame
                evaluation_table = evaluation_table.melt(
                    id_vars='index',
                    var_name='Periodo',
                    value_name='Valutazione')
                # Drop the 'index' column as it's not needed
                evaluation_table = evaluation_table.drop(columns='index')

                evaluation_table = evaluation_table.to_markdown()

                prompt_text = prompt_text.replace('{risultati_valutazioni}',
                                                  evaluation_table)

                access_title = candidate["Dichiaro di essere in possesso del titolo di studio richiesto per l’ammissione alla selezione:"]
                prompt_text = prompt_text.replace('{titolo_accesso}',
                                                  access_title)

                access_title_info = candidate["Indicare l'Istituto che lo ha rilasciato, la votazione riportata e la data di conseguimento"]
                prompt_text = prompt_text.replace('{dettagli_titolo_accesso}',
                                                  access_title_info)

                other_titles = candidate["Dichiaro di possedere titoli di studio ulteriori rispetto a quelli previsti per l’accesso all’Area di Funzionario/Elevata Qualificazione:"]
                prompt_text = prompt_text.replace('{altri_titoli}',
                                                  other_titles)

                other_title_info = candidate["Indicare l'Istituto che lo ha rilasciato, la votazione riportata e la data di conseguimento.1"]
                prompt_text = prompt_text.replace('{dettagli_altri_titoli}',
                                                  other_title_info)
                logger.info(f"Computing prompt: "+prompt['description'])
                prompt['output'] = llm_helper.get_hr_completion(prompt_text)
                score = re.findall(r"Punteggio: (\d+)", prompt["output"])
                try:
                    total_score += int(score[0])
                except:
                    logger.warning("Score non calcolato for prompt: " +
                                   prompt["description"] + " for profile: " + profile_id + " for resume: " + resume_id)

                analysis = {
                    "id": str(uuid.uuid4()),
                    "AnalysisId": str(uuid.uuid4()),
                    "CandidateId": candidate["id"],
                    "ProfileId": profile_id,
                    "Analysis": json.dumps(prompts),
                    "Text": cv_text,
                    "Score": total_score,
                    "AnalysisRunId": analysis_id
                }

            cosmos_client.put_analysis(analysis)
            cosmos_client.set_analysis_run_completed(analysis_id)
    except Exception as e:
        error_string = traceback.format_exc()
        logger.error(error_string)
        cosmos_client.set_analysis_run_failed(analysis_id, str(e))


def main():
    parser = argparse.ArgumentParser()

    
    parser.add_argument('--profile', type=str, required=True)
    parser.add_argument('--temperature', type=float,
                        required=True, default=0.9)
    parser.add_argument('--max-tokens', type=int, required=True, default=1500)
    parser.add_argument('--ids', type=str, required=True)

    cosmos_db = AzureCosmosDBClient()

    run_id = str(uuid.uuid4())

    args = parser.parse_args()

    logging.info("Arguments: " + str(args))
    try:
        for ids in args.ids.split(','):
            print(ids)

        cosmos_db = AzureCosmosDBClient()
        run_id = str(uuid.uuid4())

        analysis_id_list = []
        profile_id_list = []
        resume_id_id_list = []
        temperature_id_list = []
        max_tokens_list = []

        logging.info("Starting analysis run: " + run_id)
        print("Starting analysis run: " + run_id)
        for resume_id in args.ids.split(','):
            print("Starting analysis for resume: " + resume_id)
            logging.info("Starting analysis for resume: " + resume_id)
            analysis_run_id = str(uuid.uuid4())
            print("Creating analysis id: " + analysis_run_id)
            cosmos_db.create_analysis_run(
                analysis_run_id, run_id, resume_id, args.profile)
            print("Created analysis id: " + analysis_run_id)
            analysis_id_list.append(analysis_run_id)
            profile_id_list.append(args.profile)
            resume_id_id_list.append(resume_id)
            temperature_id_list.append(args.temperature)
            max_tokens_list.append(args.max_tokens)
            print(analysis_id_list)
            # analyze(analysis_run_id, args.profile, resume_id, args.temperature, args.max_tokens)

        with ProcessPoolExecutor(max_workers=2) as exe:
            result = exe.map(analyze,
                             analysis_id_list,
                             profile_id_list,
                             resume_id_id_list,
                             temperature_id_list,
                             max_tokens_list)
            exe.shutdown(wait=True)
            print("Analysis completed")
    except:
        error_string = traceback.format_exc()
        print(error_string)
        logging.error(error_string)


if __name__ == "__main__":
    main()
