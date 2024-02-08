
import pandas as pd


class DisciplinarySanctionsEvaluator:

    def __init__(self, candidate, parameters):
        self.is_sanctioned = candidate['sanctioned']

    def _calculate(self):
        if self.is_sanctioned:
            return "Il candidato è stato sanzionato disciplinarmente quindi riceve una riduzione di 15 punti sul punteggio finale\n\nPunteggio: -15"
        else:
            return "Il candidato non è stato sanzionato disciplinarmente\n\nPunteggio: 0"
    
    def get_results(self):
        return self._calculate()

class EvaluationCalculator:

    def __init__(self, candidate,parameters):
        self.evaluations = candidate['Valutazioni']
        self.parameters = parameters

    def _create_text_explanation(self, evaluation_table, evaluation_table_normalized, year_averages, year_scores):
        fields = ['Periodo', 'Anno', 'Valutazione']
        text = "\n\nIl candidato ha ottenuto le seguenti valutazioni:\n\n"
        # for row in evaluation_table.itertuples():
        #     text += f"{row.Periodo} {row.Anno}: {row.Valutazione}\n"
        text += evaluation_table[fields].to_markdown()
        text += "\n\nLe valutazioni sono state normalizzate come segue:\n\n"
        # for row in evaluation_table_normalized.itertuples():
        #     text += f"{row.Periodo} {row.Anno}: {row.Valutazione}\n"
        text += evaluation_table_normalized[fields].to_markdown()

        text += "\n\nLa media annuale delle valutazioni è stata calcolata come segue:\n\n"
        df_year_averages = pd.DataFrame(
            list(year_averages.items()), columns=['Anno', 'Media'])
        text = text+df_year_averages.to_markdown()
        # for key, value in year_averages.items():
        #     text += f"Anno {key}: {value}\n"

        text += "\n\nSulla base delle medie annue, i punteggi sono stati assegnati come segue:\n\n"
        df_year_scores = pd.DataFrame(
            list(year_scores.items()), columns=['Anno', 'Punteggio'])
        text += df_year_scores.to_markdown()
        # for key, value in year_scores.items():
        #     text += f"Anno {key}: {value}\n"

        text += "\n\nPunteggio: " + str(sum(year_scores.values()))

        return text

    def _calculate(self):
        evaluation_table = pd.DataFrame(self.evaluations, index=[0])

        # Reset the index
        evaluation_table = evaluation_table.reset_index()
        # Use melt to pivot the DataFrame
        evaluation_table = evaluation_table.melt(
            id_vars='index',
            var_name='Periodo',
            value_name='Valutazione')

        # Drop the 'index' column as it's not needed

        evaluation_table = evaluation_table.drop(columns='index')
        evaluation_table = evaluation_table[evaluation_table['Valutazione'] != '']
        evaluation_table = evaluation_table[evaluation_table['Valutazione'] != -1]
        evaluation_table['Anno'] = evaluation_table['Periodo'].str.extract(
            r'(\d{4})')
        evaluation_table['Anno'] = evaluation_table['Anno'].astype(int)
        evaluation_table_normalized = pd.DataFrame()

        index = 0
        for row in evaluation_table.itertuples():

            new_row = {}

            new_row['Anno'] = row.Anno
            new_row['Valutazione'] = row.Valutazione

            if row.Anno > 2020:
                if 'II' in row.Periodo:
                    new_row['Index'] = index
                    index += 1
                    new_row['Periodo'] = "III"+str(row.Anno)
                    evaluation_table_normalized =pd.concat([evaluation_table_normalized,pd.DataFrame(new_row, index=[0])])
                    new_row['Index'] = index
                    index += 1
                    new_row['Periodo'] = "IV"+str(row.Anno)
                    evaluation_table_normalized = pd.concat([evaluation_table_normalized,pd.DataFrame(new_row, index=[0])])
                elif 'I' in row.Periodo:
                    new_row['Index'] = index
                    index += 1
                    new_row['Periodo'] = "I"+str(row.Anno)
                    evaluation_table_normalized = pd.concat([evaluation_table_normalized,pd.DataFrame(new_row, index=[0])])
                    new_row['Index'] = index
                    index += 1
                    new_row['Periodo'] = "II"+str(row.Anno)
                    evaluation_table_normalized = pd.concat([evaluation_table_normalized,pd.DataFrame(new_row, index=[0])])
            else:

                new_row['Index'] = index
                index += 1
                new_row['Anno'] = row.Anno
                new_row['Valutazione'] = row.Valutazione*10
                new_row['Periodo'] = row.Periodo

                evaluation_table_normalized = pd.concat([evaluation_table_normalized,pd.DataFrame(new_row, index=[0])])

        year_averages = {
            '1': (evaluation_table_normalized.iloc[0]['Valutazione']+evaluation_table_normalized.iloc[1]['Valutazione']+evaluation_table_normalized.iloc[2]['Valutazione']+evaluation_table_normalized.iloc[3]['Valutazione']) / 4,
            '2': (evaluation_table_normalized.iloc[4]['Valutazione']+evaluation_table_normalized.iloc[5]['Valutazione']+evaluation_table_normalized.iloc[6]['Valutazione']+evaluation_table_normalized.iloc[7]['Valutazione']) / 4,
            '3': (evaluation_table_normalized.iloc[8]['Valutazione']+evaluation_table_normalized.iloc[9]['Valutazione']+evaluation_table_normalized.iloc[10]['Valutazione']+evaluation_table_normalized.iloc[11]['Valutazione']) / 4
        }

        year_scores = {}

        for key, value in year_averages.items():
            year_scores[key] = 0
            for evaluation_range in self.parameters['evaluation_table']:
                if value >= evaluation_range['range_min'] and value <= evaluation_range['range_max']:
                    year_scores[key] = evaluation_range['points']
                    break
            
            
            # if value >= 95 and value <= 100:
            #     year_scores[key] = 6
            # elif value >= 91 and value <= 94.99:
            #     year_scores[key] = 5.5
            # elif value >= 75 and value <= 90.99:
            #     year_scores[key] = 5
            # elif value >= 50 and value <= 74.99:
            #     year_scores[key] = 4
            # elif value >= 40 and value <= 49.99:
            #     year_scores[key] = 3
            # else:
            #     year_scores[key] = 0

        # print(year_averages)
        # print(year_scores)

        text = self._create_text_explanation(
            evaluation_table,
            evaluation_table_normalized,
            year_averages,
            year_scores)
        return text

    def get_results(self):
        return self._calculate()

class DisciplinarySanctionsEvaluatorBuilder:

    def __init__(self):
        self.candidate = None
        self.parameters = None

    def set_candidate(self, candidate):
        self.candidate = candidate
        return self
    
    def set_parameters(self, parameters):
        self.parameters = parameters
        return self

    def build(self):
        return DisciplinarySanctionsEvaluator(self.candidate,self.parameters)

class EvaluationCalculatorBuilder:

    def __init__(self):
        self.candidate = None
        self.parameters = None

    def set_candidate(self, candidate):
        self.candidate = candidate
        return self
    
    def set_parameters(self, parameters):
        self.parameters = parameters
        return self

    def build(self):
        return EvaluationCalculator(self.candidate,self.parameters)


class AnalysisHelper:

    @staticmethod
    def get_analysys_helper_builder(helper_name):

        if helper_name == "EvaluationCalculator":
            return EvaluationCalculatorBuilder()
        elif helper_name == "DisciplinaryCalculator":
            return DisciplinarySanctionsEvaluatorBuilder()
        else:
            return None
