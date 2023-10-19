import logging as logger
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from collections import OrderedDict 
import time
import json
import pandas as pd
import re
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
import io

def valutazione():
    try:
      
      # jd = st.session_state["jd"]
      cv = st.session_state["cv"]
      
      # ESTRAZIONE
      
      # with open(os.path.join('prompts','estrazione_esperienza_cv.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_esperienza_cv = file.read()

      # with open(os.path.join('prompts','estrazione_esperienza_jd.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_esperienza_jd = file.read()
      
      # with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_industry = file.read()
            
      # with open(os.path.join('prompts','estrazione_requisiti_attivita.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_attivita = file.read()
      
      # with open(os.path.join('prompts','estrazione_requisiti_certificazione.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_certificazione = file.read()
      
      # with open(os.path.join('prompts','estrazione_requisiti_lingua.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_lingua = file.read()
        
      # with open(os.path.join('prompts','estrazione_requisiti_specialistica.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_specialistica = file.read()
        
      # with open(os.path.join('prompts','estrazione_requisiti_titolo.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_titolo = file.read()
        
      # with open(os.path.join('prompts','estrazione_requisiti_trasversale.txt'),'r', encoding='utf-8') as file:
      #   prompt_estrazione_requisiti_trasversale = file.read()
        
      # with open(os.path.join('prompts','match_competenza_attivita.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_competenza_attivita = file.read()
      
      # with open(os.path.join('prompts','match_competenza_certificazione.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_competenza_certificazione = file.read()
      
      # with open(os.path.join('prompts','match_competenza_lingua.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_competenza_lingua = file.read()
      
      # with open(os.path.join('prompts','match_competenza_specialistica.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_competenza_specialistica = file.read()
        
      # with open(os.path.join('prompts','match_competenza_titolo.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_competenza_titolo = file.read()
      
      # with open(os.path.join('prompts','match_industry.txt'),'r', encoding='utf-8') as file:
      #   prompt_match_industry = file.read()
        
      # with open(os.path.join('prompts','trasformazione_requisiti_json.txt'),'r', encoding='utf-8') as file:
      #   prompt_trasformazione_requisiti_json = file.read()
      
      llm_helper = LLMHelper(temperature=0, max_tokens=4000)
      
      # import io
      # output_debug = io.StringIO()
      # output_debug.write("Inizio Procedura di Analisi")
      # output_debug.write("Job Description")
      # output_debug.write(jd)
      
      # output = []
      
      st.markdown("### CV")
      st.markdown(cv)
      
      
      # Paragrafo 1
      prompt = """Dato il seguente CV delimitato da
#####
{cv}
#####

- Calcola il punteggio per l'esperienza maturata nell'area di provenienza
secondo questa tabella:

|Anni di servizio|Punteggio|
|Da 0 fino a 1 anno|3|
|Da 1 fino a 2 anni|6|
|Da 2 fino a 3 anni|9|
|Da 3 fino a 4 anni|12|
|Da 4 fino a 5 anni|15|
|Da 5 fino a 6 anni|17|
|Da 6 fino a 7 anni|19|
|Da 7 fino a 8 anni|20|
|Da 8 fino a 9 anni|21|
|Oltre 9 anni|22|

- Il punteggio massimo non può superare i 22 punti
- Mostra il tuo ragionamento

Risposta:
      {cv}"""
      output = "1"
      # output = llm_helper.get_hr_completion(prompt.replace('{cv}', cv).replace('{jd}', jd))
      st.markdown("### Calcolo relativo al Paragrafo 1: Area di Provenienza")
      st.markdown(prompt)
      st.markdown(output)
      
      # Paragrafo 2
      prompt = """Sei il recruiter del Comune di Roma, aiuti nelle analisi di CV e aiuti a calcolare i punteggi per la classifica finale.

Dato il seguente CV delimitato da 
#####
{cv}
#####

Calcola il punteggio totale per i titoli di studio tenendo conto di queste regole:

- il punteggio totale non può superare 20 punti

- Per calcolare il punteggio per il titolo di studio utilizzato per l’accesso alle selezioni (Diploma di Scuola Superiore di Secondo Grado) usa questa tabella:

|Punteggio Diploma espresso in sessantesimi | Punteggio Diploma espresso in centesimi | Punti |
|Da 36 a 39|Da 60 a 66|1|
|Da 40 a 41|Da 67 a 69|3|
|Da 42 a 43|Da 70 a 72|3,5|
|Da 44 a 45|Da 73 a 76|4|
|Da 46 a 47|Da 77 a 79|4,5|
|Da 48 a 49|Da 80 a 82|5|
|Da 50 a 55|Da 83 a 92|5,5|
|Da 56 a 60|Da 93 a 100|6|

- Per calcolare il punteggio della valutazione del titolo di studio utilizzato per l’accesso alle selezioni (L, DL, LS o LM) usa questa tabella:

|Punteggio Titolo di studio|Punteggio (Titolo di accesso L)|Punteggio (Titolo di accesso DL, LS o LM)|
|110 e lode|10|12|
|110|9|11|
|Da 101 a 109|8|10|
|Da 91 a 100|7|9|
|Da 80 a 90|6|8|

- Per i candidati che come requisito di accesso utilizzeranno la Laurea Triennale (L) ma che fossero in possesso anche del DL, LS o LM ai fini dell’assegnazione del punteggio relativo alla valutazione del titolo di studio utilizzato come requisito per l’accesso alle selezioni di cui trattasi, verrà presa in considerazione la valutazione del titolo di studio “superiore” posseduto.

- Per ulteriori Titoli di Studio oltre il titolo utilizzato per l’ammissione alla selezione (punteggi da sommare a quello ottenuto alternativamente nelle due precedenti tabelle nell’ambito comunque del totale massimo di n. 20 punti):

|TITOLO|Punti|
|Laurea triennale|6|
|Master I livello|5|
|Possesso del diploma di laurea (DL) del previgente ordinamento universitario, laurea specialistica (LS) o laurea magistrale (LM)|8|
|Master II livello|6| 
|Dottorato di ricerca (DR)|7|
|Diploma di specializzazione (DS)|7|

Mostra il tuo ragionamento.

Risposta:
      {cv}"""
      output = "2"
      # output = llm_helper.get_hr_completion(prompt.replace('{cv}', cv).replace('{jd}', jd))
      st.markdown("### Calcolo relativo al Paragrafo 2: Titolo di Studio")
      st.markdown(prompt)
      st.markdown(output)
      
      # Paragrafo 3.1
      prompt = """
      {cv}"""
      output = "3.1"
      # output = llm_helper.get_hr_completion(prompt.replace('{cv}', cv).replace('{jd}', jd))
      st.markdown("### Calcolo relativo al Paragrafo 3.1: Competenze Professionali (1/2)")
      st.markdown(prompt)
      st.markdown(output)
      
      # Paragrafo 3.2
      prompt = """Sei il recruiter del Comune di Roma, aiuti nelle analisi di CV e aiuti a calcolare i punteggi per la classifica finale.

il profilo per il quale si sta calcolando la classifica è
{profilo}

Dato il seguente CV delimitato da 
#####
{cv}
#####

Calcola il punteggio per le Competenze professionali quali, a titolo esemplificativo, le competenze acquisite attraverso
percorsi formativi, le competenze certificate (es. competenze informatiche o linguistiche),
le competenze acquisite nei contesti lavorativi, le abilitazioni professionali.

Tieni presente le seguenti regole:

- Titoli valutabili fino ad un massimo di 9 punti

- Abilitazioni professionali conseguite mediante superamento di esame di Stato: 3 punti
- Corsi di lingua straniera non inferiore a 20 ore con certificazione e con esame finale superato: 1 punti. Massimo n. 2 corsi e Massimo n. 2 punti|

- Certificazioni di competenze digitali accreditate, secondo questa tabella
|Pekit expert (4 moduli), ICDL base (4 moduli) Eipass Basic (4 moduli)|1 punti|
|ICDL standard o full standard (7 moduli) oppure previgente Patente Europea (ECDL) ovvero eipass 7 moduli users ovvero pekit advanced| 2 punti|
e considera massimo 2 punti

- Corsi di Formazione o Aggiornamento Professionale, pubblici o privati, attinenti al profilo professionale per il quale si concorre, non inferiore a 20 ore, con esame finale superato secondo questa tabella:
|Corsi con certificazione ed esame superato, da 20 ore fino a 59 ore|0,5 punti|
|Corsi con certificazione ed esame superato, da 60 ore fino a 100 ore|1 punto|
|Corsi senza certificazione ed esame superato, da 101 a 200 ore|1,5 punti|
|Corsi senza certificazione ed esame superato, maggiori di 200 ore|2 punti|
il massimo del punteggio è 6 punti

- Pubblicazione di libri registrati codice ISBN di argomento attinente al profilo professionale per il quale si concorre: 2 punti (massimo 1 pubblicazione)

- Pubblicazione di articoli su giornali e riviste specializzate (cartacee e online) di argomento attinente al profilo professionale per il quale si concorre: 1 punto (massimo 2 articoli)

- Idoneità in selezioni a tempo indeterminato presso la Città Metropolitana ovvero anche presso altre pubbliche amministrazioni di cui all’art. 1, comma 2, del D.Lgs. n. 165/2001, per lo stesso profilo professionale oggetto della selezione o medesima categoria secondo questa tabella (Massimo 2 punti):
|Idoneità stesso profilo|1 punto|
|Idoneità profilo diverso|0,5 punti|

Mostra il tuo ragionamento.

Risposta:
      {cv}"""
      # output = llm_helper.get_hr_completion(prompt.replace('{cv}', cv).replace('{jd}', jd))
      st.markdown("### Calcolo relativo al Paragrafo 3.2: Competenze Professionali (2/2)")
      st.markdown(prompt)
      st.markdown(output)
      
      # output_debug.write("\n")
      # output_debug.write(prompt_estrazione_esperienza_cv)
      # output_debug.write("\n")
      # output_debug.write(llm_esperienza_cv_result)
      # output_debug.write("\n")
      # output_debug.write("\n")
      
      # st.info(f"Esperienza attuale in anni: {llm_esperienza_cv_result}")
      # output.append(["Anni di esperienza del candidato", llm_esperienza_cv_result, "NA"])
      
      # # ESTRAZIONE ESPERIENZA RICHIESTA JD
      # llm_esperienza_jd_result = llm_helper.get_hr_completion(prompt_estrazione_esperienza_jd.format(jd = jd, cv = cv))
      # st.markdown("### Estrazione Livello dalla Job Description")
      # st.markdown(llm_esperienza_jd_result)
      # json_data_esperienza = json.loads(llm_esperienza_jd_result)
      
      # output_debug.write(prompt_estrazione_esperienza_jd)
      # output_debug.write("\n")
      # output_debug.write(llm_esperienza_jd_result)
      # output_debug.write("\n")
      # output_debug.write("\n")
      
      # esperienza_minima = json_data_esperienza["minimo"]
      # esperienza_massima = json_data_esperienza["massimo"]
      
      # st.info(f"Esperienza richiesta in anni - Minimo : {esperienza_minima}")
      # st.info(f"Esperienza richiesta in anni - Massimo : {esperienza_massima}")
      
      # output.append(["Anni di esperienza minima richiesti dalla job description", esperienza_minima, "NA"])
      # output.append(["Anni di esperienza massima richiesti dalla job description", esperienza_massima, "NA"])

      # # ESTRAZIONE INDUSTRY
      # st.markdown("### Estrazione Industry dalla Job Description")
      # llm_industry_result = llm_helper.get_hr_completion(prompt_estrazione_industry.format(jd = jd, cv = cv))
      # st.markdown(llm_industry_result)
      
      # output_debug.write(prompt_estrazione_industry)
      # output_debug.write("\n")
      # output_debug.write(llm_industry_result)
      # output_debug.write("\n")
      # output_debug.write("\n")
      
      # industry = ""
      # match = re.search(r'\[(.*?)\]', llm_industry_result)
      # if match:
      #   industry = match.group(1)  
      # st.info(f"Industry considerata: {industry}")
      
      # # MATCH INDUSTRY
      # llm_match_industry_result = llm_helper.get_hr_completion(prompt_match_industry.format(jd = jd, cv = cv, industry = industry))
      # st.markdown("### Match Industry")
      # st.markdown(llm_match_industry_result)
      
      # output_debug.write(prompt_match_industry)
      # output_debug.write("\n")
      # output_debug.write(llm_match_industry_result)
      # output_debug.write("\n")
      # output_debug.write(industry)
      # output_debug.write("\n")
      # output_debug.write("\n")
      
      # if 'true]' in llm_match_industry_result.lower() or 'true)' in llm_match_industry_result.lower() or 'possibilmente vera' in llm_match_industry_result.lower():
      #   output.append(["Industry", industry, "1"])
      # else:
      #   output.append(["Industry", industry, "0"])
        
      # st.info(f"Risultato Industry: {llm_match_industry_result}")
      
      # time.sleep(1)
      
      # output_debug.write("Inizio Match Requisiti")
      # output_debug.write("\n")
      
      # estrazione_match_requisiti(tipologia="principali attività", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_attivita, 
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json, 
      #   prompt_match=prompt_match_competenza_attivita, 
      #   jd=jd, cv=cv)

      # estrazione_match_requisiti(tipologia="conoscenza specialistica", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_specialistica, 
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json, 
      #   prompt_match=prompt_match_competenza_specialistica, 
      #   jd=jd, cv=cv)
      
      # estrazione_match_requisiti(tipologia="conoscenza trasversale", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_trasversale,
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json,
      #   prompt_match="",
      #   jd=jd, cv=cv)
      
      # estrazione_match_requisiti(tipologia="titolo studio", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_titolo, 
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json, 
      #   prompt_match=prompt_match_competenza_titolo, 
      #   jd=jd, cv=cv)
      
      # estrazione_match_requisiti(tipologia="certificazioni", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_certificazione, 
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json, 
      #   prompt_match=prompt_match_competenza_certificazione, 
      #   jd=jd, cv=cv)

      # estrazione_match_requisiti(tipologia="lingua", output=output, output_debug=output_debug, llm_helper=llm_helper, 
      #   prompt_estrazione=prompt_estrazione_requisiti_lingua, 
      #   prompt_trasformazione=prompt_trasformazione_requisiti_json, 
      #   prompt_match=prompt_match_competenza_lingua, 
      #   jd=jd, cv=cv)
      
      # # Stampa finale
      # df = pd.DataFrame(output, columns = ['Tipologia', 'Nome', 'Obbl./Pref.',  'Match'])
      # st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
      
      # final_debug_text = output_debug.getvalue()
      # output_debug.close()
      
      # st.download_button('Scarica il file per il debug', final_debug_text)
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        # print(error_string)
        
        # output_debug.write(error_string)
        # final_debug_text = output_debug.getvalue()
        # output_debug.close()
        # st.download_button('Scarica il file per il debug', final_debug_text)

try:
  
    st.title("Analisi e Calcolo Punteggi per CV")
    profile = st.selectbox("Profilo:", ("Profilo n.1", "Profilo n.2", "Profilo n.3"))
    uploaded_cv = st.file_uploader("Caricare un CV (formato PDF)", type=['pdf'], key=1)
    if uploaded_cv is not None:
      form_client = AzureFormRecognizerClient()
      results = form_client.analyze_read(uploaded_cv)
      cv = results[0]
      st.session_state["cv"] = cv
      st.success("Il file è stato caricato con successo")
      
    st.button(label="Inizio Analisi", on_click=valutazione)

except Exception as e:
    st.error(traceback.format_exc())