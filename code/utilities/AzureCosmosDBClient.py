# This is a set of utilities to connect to a cosmos db instance on Azure.

import os
from typing import List
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv
import json
import traceback
from azure.identity import ManagedIdentityCredential
from datetime import datetime, timezone


class AzureCosmosDBClient:
    def __init__(self):
        load_dotenv()
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        if self.key:
            self.client = CosmosClient(self.endpoint, self.key)
        else:
            self.client = CosmosClient(self.endpoint, credential=ManagedIdentityCredential(
                client_id=os.getenv("APP_CONTAINER_CLIENT_ID")))
        self.database_name = os.getenv('COSMOS_DATABASE_NAME')
        self.database = self.client.get_database_client(self.database_name)
        self.container_name = 'llm'
        self.users = self.database.get_container_client('users')
        self.resumes = self.database.get_container_client('resumes')
        self.candidates = self.database.get_container_client('candidates')
        self.profiles = self.database.get_container_client('profiles')
        self.analyses = self.database.get_container_client('analyses')
        self.upload_runs = self.database.get_container_client('uploadruns')

    def put_analysis(self, analysis):
        self.analyses.upsert_item(analysis)

    def get_analysis_by_candidate_id(self, candidate_id):
        query = f"SELECT * FROM analyses a WHERE a.CandidateId = '{candidate_id}'"
        items = self.analyses.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_analysis_by_candidate_id_and_profile(self, candidate_id, profile_id):
        query = f"SELECT * FROM analyses a WHERE a.CandidateId = '{candidate_id}' AND a.ProfileId = '{profile_id}'"
        items = self.analyses.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def delete_analysis_by_candidate_id_and_profile(self, candidate_id, profile_id):
        analysis = list(self.get_analysis_by_candidate_id_and_profile(
            candidate_id, profile_id))
        for a in analysis:
            self.analyses.delete_item(a['id'], a['AnalysisId'])

    def put_candidate(self, candidate):
        self.candidates.upsert_item(candidate)

    def get_candidates(self):
        query = "SELECT * FROM candidates c"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_candidates_count(self):
        query = "SELECT VALUE COUNT(1) FROM candidates c"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        count = list(items)[0]
        return count

    def get_candidate_by_id(self, id):
        query = f"SELECT * FROM candidates c WHERE c.CandidateId = '{id}'"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_candidates_with_candidacy_count(self):
        query = "SELECT VALUE COUNT(1) FROM candidates c WHERE ARRAY_LENGTH(c.candidature) > 0"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        count = list(items)[0]
        return count

    def get_candidates_with_evaluation_count(self):
        query = "SELECT VALUE COUNT(1) FROM candidates c WHERE IS_DEFINED(c.Valutazioni)"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        count = list(items)[0]
        return count

    def get_candidates_with_history_count(self):
        query = 'SELECT VALUE COUNT(1) FROM candidates c WHERE ARRAY_LENGTH(c["Storia Rapporto Lavorativo"]) > 0'
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        count = list(items)[0]
        return count

    def get_candidate_by_cf(self, cf):
        cf = cf.upper()
        query = f"SELECT * FROM candidates c WHERE UPPER(c.CodiceFiscale) = '{cf}'"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_candidate_by_profile(self, profile):
        query = f"SELECT * FROM candidates c WHERE ARRAY_CONTAINS(c.candidature, '{profile}')"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_candidate_by_profiles(self, profiles: List[str]):
        if len(profiles) == 0:
            return []

        query = f"SELECT * FROM candidates c WHERE ARRAY_CONTAINS(c.candidature, '{profiles[0]}')"
        for profile in profiles[1:]:
            query += f" OR ARRAY_CONTAINS(c.candidature, '{profile}')"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_candidate_by_name_and_surname(self, name, surname):
        name = name.lower()
        surname = surname.lower()
        query = f"SELECT * FROM candidates c WHERE LOWER(c.Nome) = '{name}' AND LOWER(c.Cognome) = '{surname}'"
        items = self.candidates.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_resumes(self):
        query = "SELECT * FROM resumes r"
        items = self.resumes.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_resume_by_id(self, id):
        query = f"SELECT * FROM resumes r WHERE r.id = '{id}'"
        items = self.resumes.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def put_resume(self, resume):
        self.resumes.upsert_item(resume)

    def get_users(self):
        query = "SELECT * FROM users u"
        items = self.users.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_user_by_id(self, id):
        query = f"SELECT * FROM users u WHERE u.id = '{id}'"
        items = self.users.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_user(self, principal_id):
        query = f"SELECT * FROM users u WHERE u.id = '{principal_id}'"
        items = self.users.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def put_user(self, principal_id, principal_name, role, profiles):
        user = {
            "id": principal_id,
            "name": principal_name,
            "role": role,
            "profiles": profiles
        }
        self.users.upsert_item(user)

    def get_profiles(self):
        query = "SELECT * FROM profiles p"
        items = self.profiles.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_profile_by_id(self, id):
        query = f"SELECT * FROM profiles p WHERE p.profile_id = '{id}'"
        items = self.profiles.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def get_profile_by_description(self, profile_description):
        query = f"SELECT * FROM profiles p WHERE p.profile_description = '{profile_description}'"
        items = self.profiles.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def update_profile(self, profile):
        self.profiles.upsert_item(profile)

    def create_upload_run(self, id, run_id, file_name):
        upload_run = {
            "id": id,
            "run_id": run_id,
            "starting_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "ending_time": None,
            "file_name": file_name,
            "status": "pending"
        }
        self.upload_runs.upsert_item(upload_run)

    def get_batch_upload_run_ids(self):
        query = f"SELECT distinct c.run_id FROM c"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True) 
        return items

    def get_upload_run(self, id):
        query = f"SELECT * FROM uploadruns u WHERE u.id = '{id}'"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True)
        return items
    
    def get_upload_runs(self, run_id):
        query = f"SELECT * FROM uploadruns u WHERE u.run_id = '{run_id}'"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True)
        return items

    def set_upload_run_completed(self, id):
        self.set_upload_run_status(id, "completed")
        self.set_upload_run_ending_date(id)

    def set_upload_run_running(self, id):
        self.set_upload_run_status(id, "running")

    def set_upload_run_failed(self, id,error_message):
        self.set_upload_run_status(id, "failed")
        self.set_upload_run_ending_date(id)
        self.set_upload_run_error_message(id, error_message)

    def set_upload_run_status(self, id, status):
        query = f"SELECT * FROM uploadruns u WHERE u.id = '{id}'"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True)
        upload_run = list(items)[0]
        upload_run['status'] = status
        self.upload_runs.upsert_item(upload_run)

    def set_upload_run_error_message(self, id, error_message):
        query = f"SELECT * FROM uploadruns u WHERE u.id = '{id}'"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True)
        upload_run = list(items)[0]
        upload_run['error_message'] = error_message
        self.upload_runs.upsert_item(upload_run)


    def set_upload_run_ending_date(self,id):
        query = f"SELECT * FROM uploadruns u WHERE u.id = '{id}'"
        items = self.upload_runs.query_items(
            query=query, enable_cross_partition_query=True)
        upload_run = list(items)[0]
        upload_run['ending_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.upload_runs.upsert_item(upload_run)        
