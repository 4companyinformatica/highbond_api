import requests as rq
import pathlib as pl
import os
import base64
import pandas as pd
import re
from typing import Literal, List, Union
from IPython.display import display, Image

class Highbond_API:
    def __init__(
            self,
            token: str,
            organization_id: str,
            protocol: str = 'https',
            server: Literal['apis-us.highbond.com', 'apis-ca.highbond.com', 'apis-eu.highbond.com', 'apis-ap.highbond.com', 'apis-au.highbond.com', 'apis-af.highbond.com', 'apis-sa.highbond.com', 'apis.highbond-gov.com', 'apis.highbond-gov2.com'] = 'apis-us.highbond.com', 
            talkative: bool = True
        ):
        """
        Cria uma instância da classe hbapi para interação simplificada com a API Highbond.

        #### Referência: 
        - https://docs-apis.highbond.com/

        #### Parâmetros:
        - token (str): Token do Highbond obtido através do portal.
        - organization_id (str): ID da organização, coletado da URL do portal ao logar.
        - server (str): Servidor do Highbond a ser utilizado. Padrão é 'apis-us.highbond.com'.
        - talkative (bool): Se True, exibe mensagens de sucesso em requisições. Padrão é True.

        #### Opções disponíveis de servidor:
        - Estados Unidos da América: https://apis-us.highbond.com
        - Canadá: https://apis-ca.highbond.com
        - Europa: https://apis-eu.highbond.com
        - Ásia: https://apis-ap.highbond.com
        - Oceania: https://apis-au.highbond.com
        - África: https://apis-af.highbond.com
        - América do Sul: https://apis-sa.highbond.com
        - Governo Federal dos EUA: https://apis.highbond-gov.com
        - Governo Estadual dos EUA: https://apis.highbond-gov2.com
        """
        
        # CONFIGURAÇÕES DA CLASSE
        self.token = token
        self.organization_id = organization_id
        self.protocol = protocol
        self.server = server
        self.talkative = talkative

        curr_org = self.getOrganization()

        # Classes auxiliares
        self.actions = self._Actions(self)
        self.controls = self._Controls(self)
        self.entities = self._Entities(self)
        self.frameworks = self._Frameworks(self)
        self.issues = self._Issues(self)
        self.results = self._Results(self)
        self.requests = self._Requests(self)
        self.risks = self._Risks(self)
        self.objectives = self._Objectives(self)
        self.planningFiles = self._PlanningFiles(self)
        self.projects = self._Projects(self)
        self.robots = self._Robots(self)
        self.strategy = self._Strategy(self)
        self.toDos = self._ToDos(self)
        self.users = self._Users(self)
        self.walkthroughs = self._Walkthroughs(self)
        
            
        def is_jupyter_nb() -> bool:
            try:
                from IPython import get_ipython
                return get_ipython() is not None
            except ImportError:
                return False

        if bool(curr_org):

            if self.talkative:
                print(f"Classe instanciada para a organização {self.organization_id}\n"\
                      f"\tNome: {curr_org['data']['attributes']['name']}\n"\
                      f"\tRegião: {curr_org['data']['attributes']['region']}\n"\
                      f"\tFuso horário: {curr_org['data']['attributes']['timezone']}\n")
                if is_jupyter_nb():
                    display(Image(curr_org['data']['attributes']['small_logo']))
    
    def validate_response(self, response: rq.Response) -> dict | Exception:
        if response.status_code == 200:
            if self.talkative == True:
                print('Código: 200\nMensagem: Requisição executada com sucesso\n')
            return response.json()
        elif response.status_code == 201:
                if self.talkative == True:
                    print('Código: 201\nMensagem: Criado\n')
                return response.json()
        elif response.status_code == 202:
            if self.talkative == True:
                print('Código: 202\nMensagem: Aceito\n')
            return f"Resposta da API: {response.text}"
        elif response.status_code == 400:
            raise Exception(f'Código: 400\nMensagem: Falha na requisição API -> {response.text}')
        elif response.status_code == 401:
            raise Exception(f'Código: 401\nMensagem: Falha na autenticação com token -> {response.text}')
        elif response.status_code == 403:
            raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {response.text}')
        elif response.status_code == 404:
            raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {response.text}')
        elif response.status_code == 415:
            raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {response.text}')
        elif response.status_code == 422:
            raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {response.text}')
        else:
            raise Exception('Falha desconhecida.')

    def requester(self, method: str, url: str, headers: dict, params: dict = {}, json: dict = {}, files: dict = {}) -> dict | None:
        """Faz qualquer requisição HTTP e centraliza try/except + validação"""
        try:
            if self.talkative:
                print(f"Iniciando a requisição HTTP [{method.upper()}]...")

            response = rq.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                files=files
            )

            return self.validate_response(response)

        except Exception as e:
            print(f"A requisição não foi possível:\n{e}")
            return None

    def get_command(self, api_url: str, api_headers: dict, api_params: dict = {}) -> dict | None:
        return self.requester("GET", api_url, api_headers, params=api_params)

    def post_command(self, api_url: str, api_headers: dict, api_params: dict = {}, api_schema: dict = {}, api_files: dict = {}) -> dict | None:
        return self.requester("POST", api_url, api_headers, params=api_params, json=api_schema, files=api_files)

    def patch_command(self, api_url: str, api_headers: dict, api_params: dict = {}, api_schema: dict = {}) -> dict | None:
        return self.requester("PATCH", api_url, api_headers, params=api_params, json=api_schema)

    def delete_command(self, api_url: str, api_headers: dict, api_params: dict = {}) -> dict | None:
        return self.requester("DELETE", api_url, api_headers, params=api_params)
    
######################################

    def getOrganization(self) -> dict:
        """
        Retorna informações sobre a organização associada ao id fornecido.

        #### Referência:
        https://docs-apis.highbond.com/#operation/getOrganization
        """
        headers = {
            'Content-type': 'application/vnd.api+json',
            'Authorization': f'Bearer {self.token}'
        }
        
        url = f"{self.protocol}://{self.server}/v1/orgs/{self.organization_id}/"

        return self.get_command(api_url=url, api_headers=headers)
    
######################################

    class _Actions():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
        def getActions(self,
                    issue_id: str,
                    fields: List[Literal["title","created_at","updated_at","owner_name","owner_email","send_recurring_reminder","include_issue_details","include_remediation_details","description","due_date","priority","closed","completed_date","status","submitted_on","slug","custom_attributes","issue","assigned_by","cc_users"]] = None,
                    page_num: int = 1,
                    page_size: int = 100) -> dict:
            """
            Lista as ações de um problema da organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getActions

            #### Parâmetros:
            - fields: Define os campos que serão trazidos na requisição. O padrão é tudo
            - issue_id: Identificador único do problema.
            - page_num: Define a página atual.
            - page_size: Define a quantidade de registros retornados.

            #### Retorna:
            Um dicionário contendo informações sobre as ações do risco consultado

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getActives(fields=['title, description'], self.parent.organization_id = '1111', issue_id = '2222', page_num=1, page_size=25)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode(),
            }

            if fields:
                params['actions'] = ",".join(fields)

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/issues/{issue_id}/actions'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        def getAction(self,
                    action_id: str,
                    fields: List[Literal["title","created_at","updated_at","owner_name","owner_email","send_recurring_reminder","include_issue_details","include_remediation_details","description","due_date","priority","closed","completed_date","status","submitted_on","slug","custom_attributes","issue","assigned_by","cc_users"]] = None
                    ) -> dict:
            """
            Consulta uma ação específica de um problema da organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getAction

            #### Parâmetros:
            - fields: Define os campos que serão trazidos na requisição. O padrão é tudo
            - action_id: Identificador único da ação.
            - page_num: Define a página atual.
            - page_size: Define a quantidade de registros retornados.

            #### Retorna:
            Um dicionário contendo informações sobre as ações do risco consultado

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getActives(fields=['title, description'], self.parent.organization_id = '1111', issue_id = '2222', page_num=1, page_size=25)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {

            }

            if fields:
                params['actions'] = ",".join(fields)

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/actions/{action_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        def getActionComments(
                self,
                action_id: str,
                fields: list = ['message_content','commenter_name','commenter_email','created_at','updated_at','action','commenter_user'],
                page_num: int = 1,
                page_size: int = 100
            ) -> dict:
            """
            Retorna todos os comentários associados a uma ação.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getActionComments
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode(),
            }

            if fields:
                params['fields[action_comments]'] = ",".join(fields)

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/actions/{action_id}/comments'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Controls():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===     
        def getControls(self, 
                        parent_resource_id: str,
                        fields: list = ['title','description','control_id','owner','frequency','control_type',
                                        'prevent_detect','method','status','position','created_at','updated_at',
                                        'custom_attributes','objective','walkthrough','control_test_plan',
                                        'control_tests','mitigations','owner_user','entities','framework_origin'],
                        include: Literal['', 'objective'] = '', page_size: int = 100, page_num: int = 1) -> dict:
            """
            Lista todos os controles de um objetivo.
            """
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/objectives/{parent_resource_id}/controls'
            
            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            params = {
                "page[size]": str(page_size),
                'page[number]': base64.b64encode(str(page_num).encode()).decode(),
                "fields[controls]": ",".join(fields),
                "include": include
            }
            
            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)  

        def getAControl(self, 
                        resource_id,
                        fields: list = ['title','description','control_id','owner','frequency','control_type',
                                        'prevent_detect','method','status','position','created_at','updated_at',
                                        'custom_attributes','objective','walkthrough','control_test_plan',
                                        'control_tests','mitigations','owner_user','entities','framework_origin'],
                        include: Literal['', 'objective'] = '') -> dict:
            url = f"https://{self.parent.server}/v1/orgs/{self.parent.organization_id}/controls/{resource_id}"

            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                "fields[controls]": ",".join(fields),
                "include": include
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        def getOrganizationControls(
                self,
                fields_controls: list = ["title","description","control_id","owner","frequency","control_type","prevent_detect","method","status","position","created_at","updated_at","custom_attributes","objective","walkthrough","control_test_plan","control_tests","mitigations","owner_user","entities","framework_origin"],
                fields_objectives: list = ["title","description","reference","division_department","owner","executive_owner","created_at","updated_at","project","assigned_user","owner_user","executive_owner_user","custom_attributes","position","risk_control_matrix_id","walkthrough_summary_id","testing_round_1_id","testing_round_2_id","testing_round_3_id","testing_round_4_id","entities","framework","framework_origin","risk_assurance_data","planned_start_date","actual_start_date","planned_end_date","actual_end_date","planned_milestone_date","actual_milestone_date"],
                fields_walkthroughs: list = ["walkthrough","control_verified","original_updated_at","preparer_signoff","detail_reviewer_signoff","general_reviewer_signoff","supplemental_reviewer","specialty_reviewer","control_performance_enabled","control_performance_readonly","signed_off","readonly","locked","enabled","planned_milestone_date","actual_milestone_date"],
                fields_control_tests: list = ["assignee_name","testing_round_number","not_applicable","sample_size","testing_results","testing_conclusion","testing_conclusion_status","created_at","updated_at","control","assigned_user","actual_milestone_date","planned_milestone_date","preparer_signoff","detail_reviewer_signoff","general_reviewer_signoff","supplemental_reviewer","specialty_reviewer"],
                sort: str = None,
                filter_frequency: str = None,
                filter_owner: str = None,
                filter_walkthrough_control_design: str = None,
                filter_control_type: str = None,
                filter_status: str = None,
                filter_control_id: str = None,
                filter_id: str = None,
                page_size: int = 100,
                page_num: int = 1
            ) -> dict:
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[controls]': ','.join(fields_controls) if fields_controls else fields_controls,
                'fields[objectives]': ','.join(fields_objectives) if fields_objectives else fields_objectives,
                'fields[walkthroughs]': ','.join(fields_walkthroughs) if fields_walkthroughs else fields_walkthroughs,
                'fields[control_tests]': ','.join(fields_control_tests) if fields_control_tests else fields_control_tests,
                'sort': sort,
                'filter[walkthrough.control_design]': filter_walkthrough_control_design,
                'filter[control_type]': filter_control_type,
                'filter[status]': filter_status,
                'filter[control_id]': filter_control_id,
                'filter[id]': filter_id,
                'page[size]': str(page_size),
                'page[number]': base64.b64encode(str(page_num).encode()).decode()
            }
        
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/controls'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
    
        def getControlTests(self,
                fields: list = ['testing_round_number','not_applicable','sample_size','testing_results','testing_conclusion','testing_conclusion_status',
                                            'created_at','updated_at','custom_attributes','control','assigned_user','actual_milestone_date','planned_milestone_date'],
                sort: Literal["id", '-id', "walkthrough_results", "-walkthrough_results", "control_design", "-control_design","created_at", "-created_at", "updated_at",  "-updated_at"] = "id",
                project_id: str = None,
                project_name: str = None,
                project_state: str = None,
                project_status: str = None,
                control_id: list = None,
                control_design: str = None,
                control_title: str = None,
                control_id_interno: str = None,
                control_query: str = None,
                control_status: str = None,
                control_owner: str = None,
                control_frequency: str = None,
                control_type: str = None,
                objective_title: str = None,
                objective_reference: str = None,
                test_round_1_user_id: str = None,
                test_round_2_user_id: str = None,
                test_round_3_user_id: str = None,
                test_round_4_user_id: str = None,
                include: List[Literal["control", "control.objective"]] = None,
                page_size: int = 100,
                page_num: int = 100, 
                fields_controls: List[Literal["title","description","control_id","owner","frequency","control_type","prevent_detect","method","status",
                                                "position","created_at","updated_at","custom_attributes","objective","walkthrough","control_test_plan",
                                                "control_tests","mitigations","owner_user","entities","framework_origin"]] = None,
                fields_objectives: List[Literal["title","description","reference","division_department","owner","executive_owner","created_at","updated_at",
                                                        "project","assigned_user","custom_attributes","position","risk_control_matrix_id","walkthrough_summary_id",
                                                        "testing_round_1_id","testing_round_2_id","testing_round_3_id","testing_round_4_id","entities","framework",
                                                        "framework_origin","risk_assurance_data","planned_start_date","actual_start_date","planned_end_date","actual_end_date",
                                                        "planned_milestone_date","actual_milestone_date"]] = None
                ) -> str:
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[control_tests]': ','.join(fields),
                'sort': sort,
                'filter[project.id]': project_id,
                'filter[project.name]': project_name,
                'filter[project.state]': project_state,
                'filter[project.status]': project_status,
                'filter[control.id]': ','.join(control_id) if control_id else control_id,
                'filter[control_design]': control_design,
                'filter[control.title]': control_title,
                'filter[control.control_id]': ','.join(control_id_interno) if control_id_interno else control_id_interno,
                'filter[control.query]': control_query,
                'filter[control.status]': control_status,
                'filter[control.owner]': control_owner,
                'filter[control.frequency]': control_frequency,
                'filter[control.control_type]': control_type,
                'filter[objective.title]': objective_title,
                'filter[objective.reference]': objective_reference,
                'filter[control.control_tests.1.assigned_user.id]': test_round_1_user_id,
                'filter[control.control_tests.2.assigned_user.id]': test_round_2_user_id,
                'filter[control.control_tests.3.assigned_user.id]': test_round_3_user_id,
                'filter[control.control_tests.4.assigned_user.id]': test_round_4_user_id,
                'include': ','.join(include) if include else include,
                'fields[controls]': ','.join(fields_controls) if fields_controls else fields_controls,
                'fields[objectives]': ','.join(fields_objectives) if fields_objectives else fields_objectives,
                'page[size]': str(page_size),
                'page[number]': base64.b64encode(str(page_num).encode()).decode(),
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/control_tests'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        def getAControlTest(self,
                resource_id: str,
                fields: list = ['assignee_name','testing_round_number','not_applicable','sample_size','testing_results','testing_conclusion','testing_conclusion_status',
                                'created_at','updated_at','control','assigned_user','actual_milestone_date','planned_milestone_date','preparer_signoff',
                                'detail_reviewer_signoff','general_reviewer_signoff','supplemental_reviewer','specialty_reviewer'],
                include: List[Literal["control", "control.objective"]] = None,
            ) -> str:
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[control_tests]': ','.join(fields),
                'include': ','.join(include) if include else include,
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/control_tests/{resource_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
            # === POST ===
            
            # === PATCH ===
            
            # === DELETE ===
         
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===
    
    class _Entities():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getEntities(self,
                fields_entities: str = 'title,description,created_at,updated_at,parent,children_count,entity_category',
                page_size: int = 100,
                page_num: int = 1
                ) -> dict:
            """
            Retorna todas as entidades (entities) da organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getEntities

            #### Parâmetros:
            - fields_entities: parâmetro que define quais campos serão retornados na API (padrão é tudo)
            - page_size: parâmetro que define a quantidade de registros que retornará a cada consulta
            - page_num: parâmetro que seleciona a página de resposta (se a quantidade total de registros ultrapassar page_size)
            
            """
            

            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[entities]': fields_entities,
                'page_size': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/entities'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Frameworks():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getFrameworks(self,
                    fields: list = ['name','created_at','updated_at','folder_name','description','project_type'],
                    page_size: int = 100,
                    page_num: int = 1
                ) -> dict:
            
            url = f"{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/frameworks"
        
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
        
            params = {
                "fields[frameworks]": ",".join(fields),
                "page[size]": page_size,
                'page[number]': base64.b64encode(str(page_num).encode()).decode()
            }
        
            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Issues():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getOrgIssues(self, 
                        fields: List[Literal["title", "description", "creator_name", "created_at", "updated_at", "position", "owner", "recommendation", "deficiency_type", "severity", "published", "identified_at", "reference", "reference_prefix", "risk", "scope", "escalation", "cause", "effect", "cost_impact", "executive_summary", "executive_owner", "project_owner", "closed", "remediation_status", "remediation_plan", "remediation_date", "actual_remediation_date", "retest_deadline_date", "actual_retest_date", "retesting_results_overview", "custom_attributes", "project", "entities", "target", "owner_user", "executive_owner_user", "project_owner_user", "creator_user"]] = None,
                        page_num: int = 1,
                        page_size: int = 100,
                        filter_project_id: str = None,
                        filter_project_state: Literal["active", "archive"] = "active",
                        filter_target_type: Literal["objectives","projects","project_files","issues","objectives","narratives","walkthroughs","walkthrough_summaries","testing_rounds","controls","risks","risk_control_matrices","control_tests","control_test_plans","project_results","project_plannings","accounts","test_plans"] = None,
                        filter_target_id: int = None,
                        filter_closed: bool = None,
                        sort: str = None
                        ) -> dict:
            """
            Lista os Problemas de uma organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getOrgIssues

            #### Parâmetros:
            - fields: Define os campos que serão trazidos na requisição. O padrão é tudo
            - page_size: Define a quantidade de registros trazidos, o mínimo é 25 e o máximo 100
            - page_num: Define a página que será trazida (caso a quantidade de registrso ultrapasse page_size)

            #### Retorna:
            Um dicionário contendo informações sobre os Problemas de uma organização do Highbond

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getOrgIssues(fields='title, description', page_size=25, page_num=1)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'filter[project.id]': filter_project_id,
                'filter[project.state]': filter_project_state,
                'filter[target.type]': filter_target_type,
                'filter[target.id]': filter_target_id,
                'filter[closed]': filter_closed,
                'sort': sort,
                'fields[issues]': ','.join(fields) if fields else '',
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/issues'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Results():
            def __init__(self, parent):
                self.parent = parent
                
            # === GET ===  
            def getTables(self, analysis_id: int) -> dict:

                headers = {
                    'Content-type': 'application/vnd.api+json',
                    'Authorization': f'Bearer {self.parent.token}'
                }
                
                url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/analyses/{analysis_id}/tables'

                return self.parent.get_command(api_url=url, api_headers=headers)
            
            def getCollections(self) -> dict:
                headers = {
                    'Content-type': 'application/vnd.api+json',
                    'Authorization': f'Bearer {self.parent.token}'
                }

                url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/collections'

                return self.parent.get_command(api_url=url, api_headers=headers)
            
            def getAnalyses(self, collection_id: str) -> dict:
                headers = {
                    'Content-type': 'application/vnd.api+json',
                    'Authorization': f'Bearer {self.parent.token}'
                }

                url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/collections/{collection_id}/analyses'

                return self.parent.get_command(api_url=url, api_headers=headers)
            
            def getRecords(self, table_id: int, status: str = None, assignee: str = None) -> dict:
                """
                Recebe uma tabela do módulo de resultados do highbond

                #### Referência:
                (getRecords)[https://docs-apis.highbond.com/#operation/getRecords]
                
                #### Parâmetros:
                - page_size: parâmetro que define a quantidade de registros retornados
                
                #### Retorna:
                Um dicionário contendo informações sobre o segmento do risco estratégico consultado consultado

                #### Exceções:
                - Sobe exceção se o ambiente não estiver definido corretamente.
                - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
                - Sobe exceção se houver uma falha desconhecida.

                #### Exemplo de uso:
                ```python
                instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
                result = instance.getRecords(fields='title, description', page_size=25, page_num=1)
                ```

                #### Observações:
                - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
                - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
                """
                headers = {
                    'Content-type': 'application/vnd.api+json',
                    'Authorization': f'Bearer {self.parent.token}'
                }

                params = {
                    'filter[metadata.status][]': status,
                    'filter[metadata.assignee]': assignee
                }

                if type(table_id) == int or type(table_id) == float:
                    table_id = str(table_id)

                url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/tables/{table_id}/records'
                return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
            
            # === POST ===
            def uploadRecords(self, table_id: str, input_data: pd.DataFrame, explicit_field_types: dict = {}, overwrite: bool = False) -> dict:
                """
                Faz o upload de registros para uma tabela do módulo de resultados do highbond.

                #### Referência:
                https://docs-apis.highbond.com/#operation/uploadRecords

                #### Parâmetros:
                - input_data (obrigatório): (pd.DataFrame) Recebe um dataframe com os dados a serem carregados na tabela
                - overwrite (obrigatório): (bool) Define se os dados vão substituir a tabela atual ou acrescentar a ela
                - explicit_field_types (opcional): (dict) Dicionário que força um tipo de campo do highbond para um campo de 'input_data', 
                os campos podem ser dos tipos 'character', 'numeric', logical', 'date', 'time' e 'datetime'

                #### Retorna:
                Um dict com informações sobre os dados carregados

                #### Exceções:
                - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
                - Sobe exceção se houver uma falha desconhecida.

                #### Exemplo de uso:
                ```python

                instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')

                dfCustom = pd.DataFrame(
                    {
                        'A': '1234',
                        'B': 'custom text'
                    }, 
                    index=[0]
                )
                result = instance.uploadRecords(input_data=dfCustom, overwrite=True, explicit_field_types = {'A': 'numeric'})

                ```

                #### Observações:
                - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
                - Esse método depende da biblioteca externa 'Pandas'
                """
                headers = {
                    'Accept': 'application/vnd.api+json',
                    'Authorization': f'Bearer {self.parent.token}'
                }

                # Remove campos de metadados e extras
                input_data = input_data[[field for field in input_data.columns if not re.search(r'(metadata\.|extras\.)', field)]]

                def map_dtype(
                        field: str, 
                        explicit_field_types: dict, 
                        field_type: str = object
                        ) -> str:
                    if field in explicit_field_types:
                        return explicit_field_types[field]
                    
                    elif pd.api.types.is_object_dtype(field_type):
                        return 'character'
                    
                    elif pd.api.types.is_numeric_dtype(field_type):
                        return 'numeric'
                    
                    elif pd.api.types.is_bool_dtype(field_type):
                        return 'logical'
                    
                    elif pd.api.types.is_datetime64_any_dtype(field_type):
                        return 'datetime'
                    
                    elif pd.api.types.is_timedelta64_dtype(field_type):
                        return 'time'
                    
                    else:
                        return 'unknown'
                
                columns = {}
                for col, dtype in input_data.dtypes.items():
                    columns[col] = map_dtype(field=col, field_type=dtype, explicit_field_types=explicit_field_types)

                    if pd.api.types.is_datetime64_any_dtype(dtype):
                        input_data[col] = input_data[col].astype('string').fillna("")
                        input_data[col] = input_data[col].apply(lambda x: str(x))
                    if pd.api.types.is_timedelta64_dtype(dtype):
                        input_data[col] = input_data[col].astype('string').fillna("")
                        input_data[col] = input_data[col].apply(lambda x: str(x))


                schema = {
                    'data': {
                        'columns': columns,
                        'records': input_data.to_dict(orient='records')
                    },
                    'options': {
                        'purge': overwrite
                    }
                }

                url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/tables/{table_id}/upload'

                return self.parent.post_command(api_url=url, api_headers=headers, api_schema=schema)
            
            # === PATCH ===
            
            # === DELETE ===
             
    class _Requests():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
        def getOrgRequestItems(
                self, 
                id: str = '',
                fields: list = ["created_at","updated_at","description","owner","owner_email","received","request_item_status","requestor","due_date","send_recurrent_notifications","email_subject","email_message","position","project_type","owner","project","owner_user","requestor_user","cc_users","cc_contacts","contact_reference_name","contact_reference_email","contact_reference_table_id","contact_reference_record_id","target"],
                page_size: int = 100,
                page_num: int = 1,
                sort: Literal["id", "created_at", "updated_at", "description", "owner", "owner_email", "received", "requestor", "due_date", "send_recurrent_notifications", "email_subject", "email_message", "position", "-id" "-created_at" "-updated_at" "-description" "-owner" "-owner_email" "-received" "-requestor" "-due_date" "-send_recurrent_notifications" "-email_subject" "-email_message" "-position"] = "id",
                filter_project_name : str = None,
                filter_project_id : str = None,
                filter_project_status : str = None,
                filter_target_id : str = None,
                filter_target_type : str = None,
                filter_received : Literal["true", "false"] = None,
            ) -> dict:
            """
            Lista todas as solicitações da organização ou uma em específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getOrgRequestItems \n
            https://docs-apis.highbond.com/#operation/getRequestItem

            #### Parâmetros:

            #### Retorna:

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:

            #### Observações:
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/request_items/{id}'
                
            params = {
                'fields[projects]': ','.join(fields),
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode(),
                'sort': sort,
                'filter[project.name]': filter_project_name,
                'filter[project.id]': filter_project_id,
                'filter[project.status]': filter_project_status,
                'filter[target_id]': filter_target_id,
                'filter[target_type]': filter_target_type,
                'filter[received]': filter_received,
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
         
        def getRequestStatuses(self,
                project_type_id,
                fields: list = ['status','action','default']
            ) -> dict:
            """
            Consulta todos os status de itens de requisição associados a um tipo de projeto.
            
            #### Referência:
            https://docs-apis.highbond.com/public.html#operation/getRequestItemStatuses

            #### Parâmetros:
            - project_type_id: (str) define o project_type_id que será trazido através do id
            - fields: define os campos que serão trazidos

            #### Retorna:
            Um dicionário contendo informações dos status de itens de requisição associados a um tipo de projeto

            #### Exceções:
            - Sobe exceção se o id não for encontrado.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instancia = Highbond_API(self.parent.token='seu_self.parent.token', organization_id='id_da_organização', self.parent.server='id_do_servidor', talkative=False)
            resp = instancia.getRequestStatuses(project_type_id='project_type_id')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/project_types/{project_type_id}/request_item_statuses'
            
            headers = {
                'Content-Type':'application/vnd.api+json',
                'Authorization':f'Bearer {self.parent.token}'
            }
            
            params = {
                "field[request_item_statuses]":','.join(fields)
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Risks():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getARisk(self, resource_id,
                    fields: list = ['title','description','risk_id','owner','position','impact','likelihood','custom_attributes',
                                    'custom_factors','created_at','updated_at','objective','mitigations','owner_user','entities','framework_origin','risk_assurance_data'],
                    include: Literal['', 'objective'] = '') -> dict:
    
            url = f"{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/risks/{resource_id}"

            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                "fields[risks]": ",".join(fields),
                "include": include
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params) 
   
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===
    
    class _Objectives():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getObjective(self,
                objective_id: str,
                fields: List[Literal['title','description','reference','division_department',
                                    'owner','executive_owner','created_at','updated_at',
                                    'project','assigned_user','custom_attributes','position',
                                    'risk_control_matrix_id','walkthrough_summary_id',
                                    'testing_round_1_id','testing_round_2_id','testing_round_3_id','testing_round_4_id',
                                    'entities','framework','framework_origin','risk_assurance_data',
                                    'planned_start_date','actual_start_date','planned_end_date','actual_end_date',
                                    'planned_milestone_date','actual_milestone_date']] = [
                                        'title','description','reference','division_department',
                                        'owner','executive_owner','created_at','updated_at',
                                        'project','assigned_user','custom_attributes','position',
                                        'risk_control_matrix_id','walkthrough_summary_id',
                                        'testing_round_1_id','testing_round_2_id','testing_round_3_id','testing_round_4_id',
                                        'entities','framework','framework_origin','risk_assurance_data',
                                        'planned_start_date','actual_start_date','planned_end_date','actual_end_date',
                                        'planned_milestone_date','actual_milestone_date'
                                        ]
                ) -> dict:
            
            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                "fields[objectives]": ",".join(fields)
            }

            url = f"{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/objectives/{objective_id}"

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
            
        def getObjectives(self, 
                        parent_resource_type: Literal['frameworks', 'projects'], 
                        parent_resource_id: str,
                        fields: list = ['title','description','reference','division_department','owner','executive_owner',
                            'created_at','updated_at','project','assigned_user','custom_attributes','position','risk_control_matrix_id','walkthrough_summary_id','testing_round_1_id','testing_round_2_id',
                            'testing_round_3_id','testing_round_4_id','entities','framework','framework_origin','risk_assurance_data','planned_start_date','actual_start_date',
                            'planned_end_date','actual_end_date','planned_milestone_date','actual_milestone_date'],
                        page_size=100,
                        page_num=1) -> dict: 
            """
            Lista os objetivos de um projeto ACL.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getObjectives

            #### Parâmetros:
            - page_size: parâmetro que define a quantidade de registros retornados

            #### Retorna:
            Um dicionário contendo informações sobre o segmento do risco estratégico consultado consultado

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getObjectives(fields='title, description', page_size=25, page_num=1)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            url = f"{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/{parent_resource_type}/{parent_resource_id}/objectives"

            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                "page[size]": page_size,
                'page[number]': base64.b64encode(str(page_num).encode()).decode(),
                "fields[objectives]": ",".join(fields)
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
    
        def getObjectiveRisks(self,
                parent_resource_id: str,
                fields: list = ['title','description','risk_id','owner','position','impact','likelihood','custom_attributes',
                                'custom_factors','created_at','updated_at','objective','mitigations','owner_user','entities','framework_origin','risk_assurance_data'],
                include: Literal['', 'objective'] = '', page_size=100, page_num=1
            ) -> dict:
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
    
            url = f"{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/objectives/{parent_resource_id}/risks"

            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                "page[size]": page_size,
                'page[number]': base64.b64encode(str(page_num).encode()).decode(),
                "fields[risks]": ",".join(fields),
                "include": include
            }

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params) 

        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===
        
    class _PlanningFiles():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getPlanningFiles(self,
                            parent_resource_type: Literal["projects", "frameworks"],
                            parent_resource_id: str,
                            fields: list = ['name','reference_id','description','position','created_at','updated_at','custom_attributes','project','framework','planned_start_date','actual_start_date','planned_end_date','actual_end_date','planned_milestone_date','actual_milestone_date'],
                            page_size=100,
                            page_num=1) -> dict:
            """
            Consulta arquivos de planejamento (planning_files) associados a projetos ou frameworks na organização.

            #### Referência:
            https://docs-apis.highbond.com/#tag/Planning-files

            #### Parâmetros:
            - **parent_resource_type** (`Literal["projects", "frameworks"]`): Tipo do recurso pai (projeto ou framework) ao qual os arquivos de planejamento estão vinculados.
            - **parent_resource_id** (`str`): Identificador único do recurso pai.
            - **fields** (`list`): Lista de campos a serem retornados na resposta. Padrão inclui campos essenciais como `name`, `reference_id`, `custom_attributes`, datas planejadas e reais.
            
            ##### Paginação:
            - **page_size** (`int`): Quantidade máxima de registros por página. Padrão: 100.
            - **page_num** (`int`): Número da página a ser retornada. Padrão: 1 (codificado em Base64 para compatibilidade com a API).

            #### Retorno:
            - `dict`: Dicionário contendo os arquivos de planejamento recuperados com base nos parâmetros fornecidos.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver corretamente definido (ex: `self.parent.token`, `organization_id`, `self.parent.server`).
            - Sobe exceção se a requisição falhar com código HTTP diferente de `200`.
            - Sobe exceção genérica para falhas inesperadas na execução da chamada API.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getPlanningFiles(parent_resource_type='projects', parent_resource_id='12345')
            ```

            #### Observações:
            - A resposta pode conter dados vinculados a projetos ou frameworks, conforme especificado.
            - Verifique se os campos informados no parâmetro `fields` estão disponíveis para o recurso selecionado.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
            'fields[planning_files]': ','.join(fields),
            'page[size]': str(page_size),
            'page[number]': base64.b64encode(str(page_num).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/{parent_resource_type}/{parent_resource_id}/planning_files'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
    
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    class _Projects():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getProjects(
                        self, 
                        fields: str = 'name,state,status,created_at,updated_at,description,background,budget,position,header_alert_enabled,header_alert_text,certification,control_performance,risk_assurance,management_response,max_sample_size,number_of_testing_rounds,opinion,opinion_description,purpose,scope,start_date,target_date,tag_list,project_type,entities,collaborators,risk_assurance_data,collaborator_groups,time_spent,progress,planned_start_date,actual_start_date,planned_end_date,actual_end_date,planned_milestone_date,actual_milestone_date',
                        page_size: int = 100,
                        page_num: int = 1,
                        filter_name: str = None,
                        filter_status: str = None) -> dict:
            """
            Lista os Projetos de uma organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getProjects

            #### Parâmetros:
            - fields: Define os campos que serão trazidos na requisição. O padrão é tudo
            - page_size: Define a quantidade de registros trazidos, o mínimo é 25 e o máximo 100
            - page_num: Define a página que será trazida (caso a quantidade de registrso ultrapasse page_size)

            #### Retorna:
            Um dicionário contendo informações sobre os Projetos de uma organização do Highbond

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getProjects(fields='title, description', page_size=25, page_num=1)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[projects]': fields,
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode(),
                'filter[name]': filter_name,
                'filter[status]': filter_status
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getProject(self,
                project_id: str,
                fields: str = 'name,state,status,created_at,updated_at,description,background,budget,position,header_alert_enabled,header_alert_text,certification,control_performance,risk_assurance,management_response,max_sample_size,number_of_testing_rounds,opinion,opinion_description,purpose,scope,start_date,target_date,tag_list,project_type,entities,collaborators,risk_assurance_data,collaborator_groups,time_spent,progress,planned_start_date,actual_start_date,planned_end_date,actual_end_date,planned_milestone_date,actual_milestone_date'
            ) -> dict:
            """
            Enumera as propriedades detalhadas de um projeto específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getProject

            #### Parâmetros:
            - project_id: define o projeto que será trazido através do id
            - fields: Define os campos que serão trazidos na requisição. O padrão é tudo

            #### Retorna:
            Um dicionário contendo informações sobre os Projetos de uma organização do Highbond

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getProject(project_id = 123456, fields='title, description')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[projects]': fields,
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects/{project_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getSignOffs(self,
                fields: list = ['created_at','updated_at','prepared_at','detail_reviewed_at','general_reviewed_at','supplemental_reviewed_at','specialty_reviewed_at',
                                'project','target','preparer','detail_reviewer','general_reviewer','supplemental_reviewer','specialty_reviewer','next_reviewer'],
                include: List[Literal["preparer","detail_reviewer","general_reviewer","supplemental_reviewer","specialty_reviewer","next_reviewer","target","project"]] = None,
                project_id: str = None,
                project_state: str = None,
                target_type: Literal[
                                "objectives","projects","project_files","issues","narratives","walkthroughs","walkthrough_summaries","testing_rounds","controls","risks","risk_control_matrices","control_tests","control_test_plans","project_results","project_plannings","accounts","test_plans"
                            ] = None,
                target_id: str = None,
                preparer_id = None,
                detail_reviewer_id = None,
                general_reviewer_id = None,
                supplemental_reviewer_id = None,
                specialty_reviewer_id = None,
                next_reviewer_id = None,
                page_size: int = 100,
                page_num: int = 1
                ) -> dict:
            """
            Consulta aprovações (sign-offs) vinculadas a projetos da organização.

            #### Referência:
            https://docs-apis.highbond.com/#tag/Sign-offs

            #### Parâmetros:
            Todos os parâmetros são opcionais.

            - **fields** (`list`): Lista de campos a serem retornados na resposta. Por padrão, traz todos os campos principais.
            - **include** (`List[Literal]`): Lista de entidades relacionadas a serem incluídas na resposta (ex: reviewer, project, etc).
            
            ##### Filtros:
            - **project_id** (`str`): Filtra os sign-offs por ID do projeto.
            - **project_state** (`str`): Filtra os sign-offs com base no estado do projeto.
            - **target_type** (`Literal`): Tipo do artefato alvo (ex: narratives, test_plans, issues, etc).
            - **target_id** (`str`): Identificador único do artefato alvo.
            - **preparer_id** (`str`): Filtra os sign-offs preparados por um usuário específico.
            - **detail_reviewer_id** (`str`): Filtra pelos sign-offs revisados no nível de detalhe.
            - **general_reviewer_id** (`str`): Filtra pelos sign-offs revisados no nível geral.
            - **supplemental_reviewer_id** (`str`): Filtra pelos sign-offs com revisão suplementar.
            - **specialty_reviewer_id** (`str`): Filtra pelos sign-offs com revisão especializada.
            - **next_reviewer_id** (`str`): Filtra pelos sign-offs aguardando próxima revisão.
            
            ##### Paginação:
            - **page_size** (`int`): Número máximo de registros por página. Padrão: 100.
            - **page_num** (`int`): Número da página a ser retornada. Padrão: 1.

            #### Retorno:
            - `dict`: Dicionário contendo os dados paginados dos sign-offs encontrados com base nos filtros fornecidos.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de `200`.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getSignOffs()
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
            'fields[signoffs]': ','.join(fields),
            'include': ','.join(include) if include else include,
            'page[size]': str(page_size),
            'page[number]': base64.b64encode(str(page_num).encode()).decode(),
            'filter[project.id]': project_id,
            'filter[project.state]': project_state,
            'filter[target.id]': target_id,
            'filter[target.type]': target_type,
            'filter[preparer.id]': preparer_id,
            'filter[detail_reviewer.id]': detail_reviewer_id,
            'filter[general_reviewer.id]': general_reviewer_id,
            'filter[supplemental_reviewer.id]': supplemental_reviewer_id,
            'filter[specialty_reviewer.id]': specialty_reviewer_id,
            'filter[next_reviewer.id]': next_reviewer_id,
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/signoffs'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        # === POST ===
        def createProject(
                self,
                name: str,
                start_date: str,
                target_date: str,
                project_type_id: str,
                budget: int,
                fields: str = 'name,state,status,created_at,updated_at,description,background,budget,position,header_alert_enabled,header_alert_text,certification,control_performance,risk_assurance,management_response,max_sample_size,number_of_testing_rounds,opinion,opinion_description,purpose,scope,start_date,target_date,tag_list,project_type,entities,collaborators,risk_assurance_data,collaborator_groups,time_spent,progress,planned_start_date,actual_start_date,planned_end_date,actual_end_date,planned_milestone_date,actual_milestone_date',
                status: str = "active",
                state: Literal["active", "archived"] = "active",
                description: str = None,
                background: str = None,
                management_response: str = None,
                max_sample_size: int = 0,
                number_of_testing_rounds: int = 0,
                opinion: str = None,
                opinion_description: str = None,
                purpose: str = None,
                scope: str = None,
                tag_list: List[str] = []
        ) -> dict:
            """
            Cria um projeto em uma organização

            #### Referência:
            https://docs-apis.highbond.com/#operation/createProject

            #### Parâmetros:
            - name (obrigatório): o nome do projeto
            - start_date (obrigatório): a string de data com o início do projeto, o formato é 'yyyy-mm-dd'
            - target_date (obrigatório): a string de data com o fim proposto do projeto, o formato é 'yyyy-mm-dd'
            - project_type_id: o id da metodologia que será associada ao projeto
            - fields: os campos que serão trazidos no dicionário de saída
            - status: campo definido pelo usuário, pode ter qualquer valor, mas os valores padrão são: "draft", "proposed", "active" e "completed"
            - state: campo que define o estado do projeto, pode ser "active" ou "archived"
            - description: define a descrição do projeto, pode ter até 524288 caracteres
            - background: define as circunstâncias que fizeram o projeto ser necessário, pode ter até 524288 caracteres
            - budget: define o orçamento para o projeto, o valor máximo é 2147483647
            - management_response: define o feedback da gerência para o projeto
            - max_sample_size: define o número máximo da amostra
            - number_of_testing_rounds: define o número de rodadas de testes no projeto
            - opinion: campo para a opinião da gerência sobre o projeto
            - opinion_description: campo com a descrição da opinião
            - purpose: propósito do projeto
            - scope: campo com a abrangência de atuação do projeto
            - tag_list: lista de strings com as tags do projeto

            #### Retorna:
            Um dict com informações sobre o projeto criado (pode ser limitado com o parâmetro "fields")

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.createRobot('nome_robô', 'descricao_robo', 'acl')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[projects]': fields
            }

            schema = {
                "data": {
                    "type": "projects",
                    "attributes": {
                        "name": name,
                        "start_date": start_date,
                        "target_date": target_date,
                        "status": status,
                        "state": state,
                        "description": description,
                        "background": background,
                        "budget": budget,
                        "management_response": management_response,
                        "max_sample_size": max_sample_size,
                        "number_of_testing_rounds": number_of_testing_rounds,
                        "opinion": opinion,
                        "opinion_description": opinion_description,
                        "purpose": purpose,
                        "scope": scope,
                        "tag_list": []
                    },
                    "relationships": {
                        "project_type": {
                            "data": {
                                "id": project_type_id,
                                "type": "project_types"
                            }
                        }
                    }
                }   
            }

            if len(tag_list) > 0:
                for tag in tag_list:
                    schema['data']['attributes']['tag_list'].append(tag)

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects'

            return self.parent.post_command(api_url=url, api_headers=headers, api_params=params, api_schema=schema)

        def createProjectEntityLink(
                self,
                project_id: str,
                entity_id: str) -> dict:
            """
            Conecta uma entidade ao projeto, marcando a mesma para toda a hierarquia inferior

            #### Referência:
            https://docs-apis.highbond.com/#operation/createProjectEntityLink

            #### Parâmetros:
            - project_id (obrigatório): (str) define o projeto que será associado
            - entity_id (obrigatório): (str) define a entidade que será associada

            #### Retorna:
            Um dict com informações sobre a entidade associada

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.createProjectEntityLink(project_id='12345', entity_id='1234')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            schema = {
                'data': {
                    'id': entity_id,
                    'type': 'entities'
                }
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects/{project_id}/entities'

            return self.parent.post_command(api_url=url, api_headers=headers, api_schema=schema)
        
        # === PATCH ===
        def updateProject(
                self, 
                project_id: str, 
                name: str,
                start_date: str,
                target_date: str,
                project_type_id: str = None,
                planned_start_date: str = None,
                planned_end_date: str = None,
                actual_start_date: str = None,
                actual_end_date: str = None,
                actual_milestone_date: str = None,
                planned_milestone_date: str = None,
                certification: bool = None,
                control_performance: bool = None,
                risk_assurance: bool = None,
                budget: int = None,
                fields: str = 'name,state,status,created_at,updated_at,description,background,budget,position,header_alert_enabled,header_alert_text,certification,control_performance,risk_assurance,management_response,max_sample_size,number_of_testing_rounds,opinion,opinion_description,purpose,scope,start_date,target_date,tag_list,project_type,entities,collaborators,risk_assurance_data,collaborator_groups,time_spent,progress,planned_start_date,actual_start_date,planned_end_date,actual_end_date,planned_milestone_date,actual_milestone_date',
                status: str = None,
                description: str = None,
                background: str = None,
                management_response: str = None,
                max_sample_size: int = None,
                opinion: str = None,
                opinion_description: str = None,
                purpose: str = None,
                scope: str = None,
                tag_list: List[str] = [],
                custom_attributes: List[dict] = [],
                entities: List[dict] = []
            ) -> dict:
            """
            Atualiza um projeto em uma organização

            #### Referência:
            https://docs-apis.highbond.com/#operation/updateProject

            """

            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[projects]': fields
            }

            schema = {
                "data": {
                    "id": project_id,
                    "type": "projects",
                    "attributes": {
                        "name": name,
                        "start_date": start_date,
                        "target_date": target_date,
                    },
                    "relationships": {
                        "project_type": {
                            "data": {
                                "id": project_type_id,
                                "type": "project_types"
                            }
                        }
                    }
                }
            }

            if bool(planned_start_date):
                schema['data']['attributes']['planned_start_date'] = planned_start_date

            if bool(planned_end_date):
                schema['data']['attributes']["planned_end_date"] = planned_end_date

            if bool(actual_start_date):
                schema['data']['attributes']["actual_start_date"] = actual_start_date

            if bool(actual_end_date):
                schema['data']['attributes']["actual_end_date"] = actual_end_date

            if bool(actual_milestone_date):
                schema['data']['attributes']["actual_milestone_date"] = actual_milestone_date

            if bool(planned_milestone_date):
                schema['data']['attributes']["planned_milestone_date"] = planned_milestone_date

            if bool(status):
                schema['data']['attributes']["status"] = status

            if bool(description):
                schema['data']['attributes']["description"] = description

            if bool(background):
                schema['data']['attributes']["background"] = background

            if bool(budget):
                schema['data']['attributes']["budget"] = budget

            if bool(certification):
                schema['data']['attributes']["certification"] = certification

            if bool(control_performance):
                schema['data']['attributes']["control_performance"] = control_performance

            if bool(risk_assurance):
                schema['data']['attributes']["risk_assurance"] = risk_assurance

            if bool(management_response):
                schema['data']['attributes']["management_response"] = management_response

            if bool(max_sample_size):
                schema['data']['attributes']["max_sample_size"] = max_sample_size

            if bool(opinion):
                schema['data']['attributes']["opinion"] = opinion

            if bool(opinion_description):
                schema['data']['attributes']["opinion_description"] = opinion_description

            if bool(purpose):
                schema['data']['attributes']["purpose"] = purpose

            if bool(scope):
                schema['data']['attributes']["scope"] = scope

            if len(tag_list) > 0:
                if not 'tag_list' in schema['data']['attributes']:
                    schema['data']['attributes']['tag_list'] = []

                for tag in tag_list:
                    schema['data']['attributes']['tag_list'].append(tag)
            
            if len(custom_attributes) > 0:
                if not 'custom_attributes' in schema['data']['attributes']:
                    schema['data']['attributes']['custom_attributes'] = []

                for custAttrib in custom_attributes:
                    schema['data']['attributes']['custom_attributes'].append(custAttrib)

            if len(entities) > 0:
                if not 'relationships' in schema['data']:
                    schema['data']['relationships'] = {}

                schema['data']['relationships']['entities'] = {}
                schema['data']['relationships']['entities']['data'] = []
                
                for entity in entities:
                    schema['data']['entities']['data'].append(entity)

            if bool(project_type_id):
                if not 'relationships' in schema['data']:
                    schema['data']['relationships'] = {}
                
                schema['data']['relationships']['project_type'] = {}
                schema['data']['relationships']['project_type']['data'] = {}
                schema['data']['relationships']['project_type']['data']['id'] = project_type_id
                schema['data']['relationships']['project_type']['data']['type'] = "project_types"

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects/{project_id}'

            # AÇÃO E RESPOSTA
            try:
                
                if self.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.patch(url, params=params, headers=headers, json=schema)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API -> {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API (Verifique se o cabeçalho está correto) -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')   

        # === DELETE ===
        def deleteProjectEntityLink(
                self,
                project_id: str,
                entity_id: str) -> dict:
            """
            Conecta uma entidade ao projeto, marcando a mesma para toda a hierarquia inferior

            #### Referência:
            https://docs-apis.highbond.com/#operation/createProjectEntityLink

            #### Parâmetros:
            - project_id (obrigatório): (str) define o projeto que será desassociado
            - entity_id (obrigatório): (str) define a entidade que será desassociada

            #### Retorna:
            Um dict com informações sobre a entidade desassociada

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.deleteProjectEntityLink(project_id='12345', entity_id='1234')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects/{project_id}/entities/{entity_id}'

            # AÇÃO E RESPOSTA
            try:
                
                if self.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.delete(url, headers=headers)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                elif Response.status_code == 201:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.talkative == True:
                        print('Código: 201\nMensagem: Criado\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                elif Response.status_code == 204:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.talkative == True:
                        print('Código: 204\nMensagem: Sem Conteúdo\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')

        def deleteProject(
                self,
                project_id: str,
                permanent: bool = False) -> dict:
            """
            Adiciona um projeto para ser deletado em 30 dias ou o deleta permanentemente

            #### Referência:
            https://docs-apis.highbond.com/#operation/deleteProject

            """
            if permanent:
                permanent_value = 'delete'
            else:
                permanent_value = None

            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'permament': permanent_value
            }
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects/{project_id}'

            return self.parent.delete_command(api_url=url, api_headers=headers, api_params=params)
           
    class _Robots:
        def __init__(self, parent):
            self.parent = parent

        # === GET ===
        def getAgents(self) -> dict:
            """
            Lista os agentes do robotics instalados na organização

            #### Referência:
            https://docs-apis.highbond.com/#operation/getAgents

            #### Retorna:
            Um dicionário contendo informações sobre os agentes do robôs.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getAgents()
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os agentes do robôs.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/agents'

            return self.parent.get_command(api_url=url, api_headers=headers)
    
        def getRobots(self) -> dict:
            """
            Lista os robôs disponíveis no robotics

            #### Referência:
            https://docs-apis.highbond.com/#operation/getRobots

            #### Retorna:
            Um dicionário contendo informações sobre os robôs.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getRobots()
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots'

            return self.parent.get_command(api_url=url, api_headers=headers)
                      
        def getRobotTasks(self, robot_id: str, environment: str) -> dict:
            """
            Lista as tarefas de um robô ACL.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/getRobotTasks

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL onde as tarefas estão armazenadas.
            - environment (str): O ambiente onde as tarefas estão armazenadas. Pode ser 'production' para o ambiente de produção ou 'development' para o ambiente de desenvolvimento.

            #### Retorna:
            Um dicionário contendo informações sobre as tarefas do robô.

            #### Exceções:
            - Raises Exception se o ambiente não estiver definido corretamente.
            - Raises Exception se a requisição API falhar com códigos de status diferentes de 200.
            - Raises Exception se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            result = instance.getRobotTasks(robot_id='123', environment='production')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo informações sobre as tarefas do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'env': environment
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_tasks'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getValues(self, task_id: str) -> dict:
            """
            Lista os valores em uma tarefa de um robô.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/getValues

            #### Parâmetros:
            - task_id (str): Id da tarefa, onde os parâmetros estão disponíveis

            #### Retorna:
            Um dicionário contendo informações sobre os parâmetros da tarefa.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            result = instance.getValues(task_id='123')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo informações sobre os jobs do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/values'

            return self.parent.get_command(api_url=url, api_headers=headers)
 
        def getSchedule(self, task_id: str) -> dict:
            """
            Informa sobre o agendamento de uma tarefa.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/getSchedule

            #### Parâmetros:
            - task_id (str): o id da tarefa

            #### Retorna:
            Um dicionário contendo informações sobre os agendamentos da tarefa

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            result = instance.getRobotJobs(task_id='123')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/schedule'

            return self.parent.get_command(api_url=url, api_headers=headers)
        
        def getRobotScriptVersion(self, robot_id: str, version_id: str, include: Literal[None, 'analytics'] = 'analytics'):
            """
            Informa sobre uma versão específica de desenvolvimentode um robô do ACL.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getRobotScriptVersion

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL.
            - version_id (str): O id da versão especificada

            #### Retorna:
            - Um dict com os dados solicitados

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getRobotScriptVersion(robot_id='123', version_id='456')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            params = {
                'include': include
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/versions/{version_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getRobotFiles(self, robot_id: str, environment: str) -> dict:
            """
            Lista os arquivos relacionados a um robô ACL em um ambiente específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getRobotFile

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL para o qual os arquivos estão armazenados.
            - environment (str): O ambiente onde os arquivos estão armazenados. Pode ser 'production' para o ambiente de produção ou 'development' para o ambiente de desenvolvimento.

            #### Retorna:
            Um dicionário contendo informações sobre os arquivos do robô.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getRobotFiles(robot_id='123', environment='production')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'env': environment
            }

            # TODO verify: ONLY ACL Robot Related Files
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_files'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
    
        def getRobotApp(self, robot_id: str, robot_app_id: str):
            """
            Informa sobre uma versão específica de desenvolvimentode um robô do ACL.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getRobotApp

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL para o qual os arquivos estão armazenados.
            - robot_app_id (str): O id da versão especificada

            #### Retorna:
            - Um dict com os dados solicitados

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getRobotApp(robot_id='123', robot_app_id='456')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_apps/{robot_app_id}'

            return self.parent.get_command(api_url=url, api_headers=headers)

        def getRobotApps(self, robot_id):
            """
            Informa sobre todas as versões de desenvolvimento de um robô do ACL.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getRobotApps

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL para o qual os arquivos estão armazenados.

            #### Retorna:
            - Um dict com os dados solicitados

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getRobotApp(robot_id='123', robot_app_id='456')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_apps'

            return self.parent.get_command(api_url=url, api_headers=headers)
        
        def getRobotJobs(self, robot_id: str, environment: str, 
                    include: list = ['robot','task','triggered_by'], 
                    page_size: int = 100, page_num: int = 1) -> dict:
            """
            Lista os jobs (execuções) de um robô ACL.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/getRobotJobs

            #### Parâmetros:
            - robot_id (str): O ID do robô ACL onde os jobs estão armazenados.
            - environment (str): O ambiente onde os jobs estão armazenados. Pode ser 'production' para o ambiente de produção ou 'development' para o ambiente de desenvolvimento.
            - include (list): Controla se os dados 'robot', 'task' e 'triggered_by' aparecem no JSON de saída. Todos os campos marcados na consulta pela classe são incluídos. Padrão é ['robot','task','triggered_by'].
            - page_size (int): Controla a quantidade de registros que aparecerão em cada consulta. Padrão é 100.
            - page_num (int): Controla o número da página. A API divide em páginas quando o número de registros ultrapassa page_size. Padrão é 1.

            #### Retorna:
            Um dicionário contendo informações sobre os jobs do robô.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            result = instance.getRobotJobs(robot_id='123', environment='production')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo informações sobre os jobs do robô.
            """
            includeCheckList = ['robot', 'task', 'triggered_by']

            if not isinstance(include, list):
                raise Exception('Precisa ser configurado no formato "list"')
            else:
                for item in include:
                    if not item in includeCheckList:
                        raise Exception(f'"{item}" não é um valor permitido para essa API')

                strInclude = ''
                for item in include:
                    strInclude = strInclude + ',' + item
                strInclude = strInclude[1:]

            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'env': environment,
                'include': strInclude,
                'page[size]': str(page_size),
                'page[number]': str(page_num)
            }
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/jobs'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def downloadFile(self, file_id: str, out_file: str) -> bytes:
            """
            Faz o download de um arquivo relacionado a um robô ACL.

            Referência:
            - https://docs-apis.highbond.com/#operation/downloadFile

            Parâmetros:
            - file_id (str): O ID do arquivo a ser baixado.
            - out_file (str): O caminho do arquivo de saída onde o conteúdo baixado será salvo.

            Retorna:
            Bytes contendo o conteúdo do arquivo baixado.

            Exceções:
            - Raises Exception se a requisição API falhar com códigos de status diferentes de 200.
            - Raises Exception se houver uma falha desconhecida.
            - Raises Exception se o arquivo não for encontrado após o download.

            Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            file_content = instance.downloadFile(file_id='123', out_file='caminho/do/arquivo/baixado.txt')
            ```

            Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de log.
            - O conteúdo do arquivo baixado é salvo no caminho especificado em 'out_file'.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_files/{file_id}/download'

            try:
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')

                Response = rq.get(url, headers=headers)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception('\nCódigo: 401\nMensagem: Falha na autenticação com self.parent.token')
                elif Response.status_code == 403:
                    raise Exception('\nCódigo: 403\nMensagem: Conexão não permitida pelo servidor')
                elif Response.status_code == 404:
                    raise Exception('\nCódigo: 404\nMensagem: Recurso não encontrado no API')
                elif Response.status_code == 415:
                    raise Exception('\nCódigo: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição')
                elif Response.status_code == 200:
                    if self.parent.talkative == True:
                        print('\nCódigo: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        
                        outPATCH = pl.Path(out_file)
                        outPATCH.write_bytes(Response.content)
                        if not os.path.exists(out_file):
                            raise Exception('\nArquivo não encontrado após o download')
                    else:
                        outPATCH = pl.Path(out_file)
                        outPATCH.write_bytes(Response.content)
                        if not os.path.exists(out_file):
                            raise Exception('\nArquivo não encontrado após o download')
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')
    
        # === POST ===
        def createRobot(self, robot_name: str, robot_description: str = None, robot_category: Literal['acl', 'highbond', 'workflow'] = 'acl') -> dict:
            """
            Cria um robô na organização

            #### Referência:
            https://docs-apis.highbond.com/#operation/createRobot

            #### Parâmetros:
            - robot_name (str): O nome do robô ACL que será criado.
            - robot_description (str): A descrição do robô.
            - robot_category (str): O topo de robô que será criado, padrão é 'acl'

            #### Retorna:
            Um dict com informações sobre o robô criado.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.createRobot('nome_robô', 'descricao_robo', 'acl')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'name': robot_name,
                'description': robot_description,
                'category': robot_category
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots'

            return self.parent.post_command(api_url=url, api_headers=headers, api_params=params)
    
        def createRobotTask(self, robot_id, environment: Literal['production', 'development'], 
                            task_name, app_version: int = None, emails_enabled: bool = False, 
                            log_enabled: bool = False, pw_crypto_key: str = None, 
                            share_encrypted: bool = False, analytic_names: list = None) -> dict:
            """
            Cria uma tarefa em um robô do Highbond, e em um ambiente específico

            #### Referência:
            https://docs-apis.highbond.com/#operation/createRobotTask

            #### Parâmetros:
            - robot_id (str): Id do robô onde a tarefa será criada
            - environment (str): define o ambiente em que a tarefa será criada
            - task_name (str): nome da tarefa que será criada
            - app_version (int): versão do robô que a tarefa vai utilizar (no caso de tarefas em produção)
            - emails_enabled (bool): Se True, habilita a notificação de e-mails da tarefa
            - log_enabled (bool): Se True, habilita a saída de logs na execução da tarefa
            - pw_crypto_key (str): define a chave de descriptografia RSA das senhas nas tarefas
            - share_encrypted(bool): define se a tarefa pode ou não ser acessada quando uma senha foi criptografada
            - analytic_names(list): define a lista de análises do robô que será executada pela tarefa

            #### Retorna:
            Um dict com informações sobre a tarefa criada.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.createRobotTask('12345', 'production', 'tarefa 1')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            schema = {
                'data':{
                    'type': 'robot_tasks',
                    'attributes': {
                        'app_version': app_version,
                        'email_notifications_enabled': emails_enabled,
                        'environment': environment,
                        'log_enabled': log_enabled,
                        'name': task_name,
                        'public_key_name': pw_crypto_key,
                        'share_encrypted': share_encrypted,
                        'analytic_names': [analytic_names]
                    }
                }
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_tasks'

            return self.parent.post_command(api_url=url, api_headers=headers, api_schema=schema)
        
        def createRobotApp(self, robot_id: str, code_page: int, comment: str, is_unicode: bool, input_file: str) -> dict:
            """
            Método que faz upload dos arquivos relacionados de um robô ACL

            #### Referência:
            - https://docs-apis.highbond.com/#operation/createRobotApp
            
            #### Parâmetros:
            - robot_id (str): id do robô
            - code_page (int): id do encoding do robô (21 - Brazil) (Ref.: https://en.wikipedia.org/wiki/Code_page)
            - comment (str): comentário da nova versão
            - is_unicode (bool): define se o projeto está na versão unicode ou não
            - input_file(str): uma string com o caminho para o arquivo .acl do projeto

            #### Retorna:
            Um dicionário contendo informações sobre o arquivo recém-criado.

            #### Exceções:
            - Raises Exception se a requisição API falhar com códigos de status diferentes de 200.
            - Raises Exception se houver uma falha desconhecida.
            - Raises Exception se a entidade for considerada improcessável (código 422).

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            result = instance.createRobotApp(
                robot_id='123', code_page=21, comment='Versão de teste ro robô', 
                is_unicode=False, input_file='caminho/do/arquivo.acl'
                )
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            schema = {
                'code_page': code_page,
                'comment': comment,
                'is_unicode': is_unicode,
                'file': open(input_file, 'rb')
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_apps'

            return self.parent.post_command(api_url=url, api_headers=headers, api_schema=schema)

        def createRobotFile(self, inputFile: str, robot_id: str, environment: Literal['production', 'development']) -> dict:
            """
            Método que faz upload dos arquivos relacionados de um robô ACL

            #### Referência:
            - https://docs-apis.highbond.com/#operation/createRobotFile
            
            #### Parâmetros:
            - inputFile (str): O caminho do arquivo a ser enviado para a API como parte da criação.
            - robot_id (str): O ID do robô ACL para o qual o arquivo será associado.
            - environment (str): O ambiente onde o arquivo será criado. Pode ser 'production' para o ambiente de produção ou 'development' para o ambiente de desenvolvimento.

            #### Retorna:
            Um dicionário contendo informações sobre o arquivo recém-criado.

            #### Exceções:
            - Raises Exception se o ambiente não estiver definido corretamente.
            - Raises Exception se a requisição API falhar com códigos de status diferentes de 200.
            - Raises Exception se houver uma falha desconhecida.
            - Raises Exception se a entidade for considerada improcessável (código 422).

            #### Exemplo de uso:
            ```python
            instance = SuaClasse()
            result = instance.createRobotFile(inputFile='caminho/do/arquivo.txt', robot_id='123', environment='production')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - O caminho do arquivo a ser enviado é especificado em 'inputFile'.
            - A resposta é um dicionário contendo informações sobre o arquivo recém-criado.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'env': environment
            }

            schema = {
                'file': open(inputFile, 'rb')
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}/robot_files'

            try:
                if not ((environment == 'production') or (environment == 'development')):
                    raise Exception('O ambiente não foi definido corretamente.')
            except Exception as e:
                print(f'A requisição não foi possível\n{e}')
                return None
            else:
                return self.parent.post_command(api_url=url, api_headers=headers, api_params=params, files=schema)
    
        def createSchedule(self, task_id: str, frequency: Literal["once", "hourly", "daily", "weekly", "monthly"], 
                            interval: int = 1, starts_at: str = None, timezone: str = None, days: List[Union[int,str]]= None) -> dict:
            """
            Cria o agendamento de uma tarefa.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/createSchedule

            #### Parâmetros:
            - task_id (str): o id da tarefa
            - frequency (str): frequência de execução do agendamento, pode ser:
                - once: Define que o agendamento só será executado uma vez
                - hourly: Define uma frequência horária (depende do intervalo)
                - daily: Define uma frequência diária (depende do intervalo)
                - weekly: Define uma frequência semanal (depende do intervalo)
                - monthly: Define uma frequência mensal (depende do intervalo)
            - interval (int): o intervalo de tempo, a unidade muda com a frequência escolhida:
                - once: Não é definido
                - hourly: define o intervalo em minutos
                - daily: define o intervalo em dias
                - weekly: define o intervalo em semanas
                - monthly: define o intervalo em meses
            - starts_at (str): datahora da primeira execução do agendamento (yyyy-mm-dd THH:MM:SS.sssZ)
            - timezone (str): fusohorário da hora definida, (America/Sao_Paulo, conforme Ref.: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
            - days (list of integers or strings): define diferentes intervalos de execução para cada frequência, exceto por "once", "hourly" e "daily"
                - weekly: em quais dias da semana o agendamento será executado, sendo 0 domingo e 6 sábado, a lista pode ter 1 ou mais dias
                - monthly: em quais dias do mês o agendamento será executado, os dias podem ser definidos entre 1 e 28. Ou "last_day" para o último dia do mês, a lista só pode ter um valor

            #### Retorna:
            Um dicionário contendo informações sobre os agendamentos da tarefa

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            instance.createSchedule('67336','daily', 2, starts_at='2024-02-17T22:00:00Z',timezone='America/Sao_Paulo')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            frequencyNullCheckList = ['once', 'hourly', 'daily']

            if frequency in frequencyNullCheckList:
                hashDays = {}
            else:
                hashDays = {'days': days}

            schema = {
                "data": {
                    "type": "schedule",
                    "attributes": {
                        "frequency": frequency,
                        "interval": interval,
                        "starts_at": starts_at,
                        "starts_at_timezone": timezone,
                        "settings": hashDays
                    }
                }
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/schedule'

            try:
                if frequency == "once":
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval != 1:
                        raise Exception('O intervalo não pode ser diferente de 1 para essa frequência')
                    
                elif frequency == 'hourly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em horas para essa frequência!')
                    
                elif frequency == 'daily':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fusohorário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')
                
                elif frequency == 'weekly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')

                    for day in days:
                        if not 0 <= day <= 6:
                            raise Exception('O parâmetro "days" não foi definido corretamente')
                
                elif frequency == 'monthly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')

                    if len(days) == 1:
                        for day in days:
                            if isinstance(day, str):
                                if not day == "last_day":
                                    raise Exception('O parâmetro "days" não foi definido corretamente')
                            else:
                                if not 1 <= day <= 28:
                                    raise Exception('O parâmetro "days" não foi definido corretamente')
                    else:
                        raise Exception('Para esta frequência, o parâmetro "days" não pode ter mais de 1 item')

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')
                return None

            return self.parent.post_command(api_url=url, api_headers=headers, api_schema=schema)
 
        def runRobotTask(self, task_id: str, include: list = ['job_values','result_tables']) -> dict:
            """
            Inicia a execução de uma tarefa de um robô no Highbond

            #### Referência:
            https://docs-apis.highbond.com/#operation/runRobotTask

            #### Parâmetros:
            - task_id (str): Id da tarefa que será executada
            - include (list): Define se os valores job_values e result_tables vão sair na resposta

            #### Retorna:
            Um dict com informações sobre a a execução da tarefa.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.runRobotTask('12345', ['job_values','result_tables'])
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            includeCheckList = ['job_values','result_tables']

            if not isinstance(include, list):
                raise Exception('Precisa ser configurado no formato "list"')
            else:
                for item in include:
                    if not item in includeCheckList:
                        raise Exception(f'"{item}" não é um valor permitido para essa API')

                strInclude = ''
                for item in include:
                    strInclude = strInclude + ',' + item
                strInclude = strInclude[1:]

            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            params = {
                'include': strInclude
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/run_now'

            return self.parent.post_command(api_url=url, api_headers=headers, api_params=params)

        # === PATCH ===
        def PATCHRobot(self, robot_id, robot_new_name: str, robot_new_description: str, robot_new_category: Literal['acl', 'highbond', 'workflow']) -> dict:
            """
            Atualiza as informações de um robô

            #### Referência:
            https://docs-apis.highbond.com/#operation/PATCHRobot

            #### Parâmetros:
            - robot_id (str): O ID do robô cujos dados serão alterados.
            - robot_new_name (str): O novo nome do robô (manter o mesmo caso não queira trocar).
            - robot_new_description (str): A nova descrição do robô (manter o mesmo caso não queira trocar)
            - robot_new_category (str): A nova categoria do robô (manter a mesma caso não queira trocar)

            #### Retorna:
            Um dicionário contendo informações sobre as alterações feitas no robô.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.PATCHRobot('novo_nome', 'nova_descricao', 'acl')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'id': robot_id,
                'name': robot_new_name,
                'description': robot_new_description,
                'category': robot_new_category
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}'

            return self.parent.patch_command(api_url=url, api_headers=headers, api_params=params)

        def PATCHRobotTask(self, task_id, environment: Literal['production', 'development'], 
                            task_name, app_version: int = None, emails_enabled: bool = False, 
                            log_enabled: bool = False, pw_crypto_key: str = None, 
                            share_encrypted: bool = False, analytic_names: list = None) -> dict:
            """
            Atualiza uma tarefa em um robô do Highbond, e em um ambiente específico

            #### Referência:
            https://docs-apis.highbond.com/#operation/PATCHRobotTask

            #### Parâmetros:
            - task_id (str): Id da tarefa que será atualizada
            - environment (str): define o ambiente em que a tarefa será atualizada
            - task_name (str): nome da tarefa que será atualizada
            - app_version (int): versão do robô que a tarefa vai utilizar (no caso de tarefas em produção)
            - emails_enabled (bool): Se True, habilita a notificação de e-mails da tarefa
            - log_enabled (bool): Se True, habilita a saída de logs na execução da tarefa
            - pw_crypto_key (str): define a chave de descriptografia RSA das senhas nas tarefas
            - share_encrypted(bool): define se a tarefa pode ou não ser acessada quando uma senha foi criptografada
            - analytic_names(list): define a lista de análises do robô que será executada pela tarefa

            #### Retorna:
            Um dict com informações sobre a tarefa atualizada.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.PATCHRobotTask('12345', 'production', 'tarefa 1')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            schema = {
                'data':{
                    'type': 'robot_tasks',
                    'attributes': {
                        'app_version': app_version,
                        'email_notifications_enabled': emails_enabled,
                        'environment': environment,
                        'log_enabled': log_enabled,
                        'name': task_name,
                        'public_key_name': pw_crypto_key,
                        'share_encrypted': share_encrypted,
                        'analytic_names': analytic_names
                    }
                }
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}'

            return self.parent.patch_command(api_url=url, api_headers=headers, api_schema=schema)

        def PATCHValues(self, task_id: str, multi_mode: bool, analytic_name: str = None, parameter_id: str = None, 
                        encrypted: bool = None, value: str = None, 
                        value_type: Literal["character","date","datetime","file","logical","number","table","time"] = None, 
                        values_list: List[list] = None) -> dict:
            """
            Atualiza o valor de um parâmetro de uma tarefa

            #### Referência:
            https://docs-apis.highbond.com/#operation/PATCHValues

            #### Parâmetros:
            - task_id (str): Id da tarefa que será atualizada
            - multi_mode (bool): Define se o método atualizará um valor ou vários valores
            - analytic_name (str): define o nome da análise que será alterada se multi_mod = False
            - parameter_id (str): define qual parâmetro será alterado se multi_mod = False
            - encrypted (bool): Se True, define que o parâmetro é protegido e mascarado como uma senha se multi_mod = False
            - value (str): conteúdo do valor que será alterado se multi_mod = False
            - value_type (str): tipo do valor que será alterado se multi_mod = False
            - values_list (list): se multi_mod = True, recebe [analytic_name, parameter_id, encrypted, value, value_type] para cada valor que será alterado

            #### Retorna:
            Um dict com informações sobre os parâmetros que serão atualizados.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso se multi_mod = False:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.PATCHValues('1234565', multi_mod=False, 'Nome da Análise', 'Nome do ParÂmetro', False, 'Novo Valor', 'character')
            ```

            #### Exemplo de uso se multi_mod = True
            ```python
                instance = hbapi('self.parent.token', 'organizacao')
                instance.PATCHValues('tarefa', multi_mod=True, values_list=[
                    ['Nome da Análise 1', 'Nome do Parâmetro 1', True, 'Novo Valor 1', 'character'], 
                    ['Nome da Análise 2', 'Nome do Parâmetro 2', True, 'Novo Valor 2', 'character']
                ]
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - Caso haja calores com senha entre os parâmetros da tarefa, PATCHValues deve sempre rodar em multi_mod=True
            pois, o parâmetro de senha deve ser passado junto dos outros.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            schema = {
                "a": ""
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/values'

            # AÇÃO E RESPOSTA
            try:

                if multi_mode == False:
                    if values_list != None:
                        schema = {
                            "data": [
                                {
                                    "type": "values",
                                    "attributes": {
                                        "analytic_name": analytic_name,
                                        "parameter_id": parameter_id,
                                        "encrypted": encrypted,
                                        "data": {
                                            "value": value,
                                            "type": value_type
                                        }
                                    }
                                }
                            ]
                        }
                    else:
                        raise Exception('"values_list" não pode ser definido se multi_mod=False')
                else:
                    if not values_list == None:
                        for item in values_list:
                            if len(item) != 5:
                                raise Exception('Um dos valores de values_list foi mal configurado')
                            schema = {
                                "data": []
                            }

                            hashTemp = {
                                    "type": "values",
                                    "attributes": {
                                        "analytic_name": item[0],
                                        "parameter_id": item[1],
                                        "encrypted": item[2],
                                        "data": {
                                            "value": item[3],
                                            "type": item[4]
                                        }
                                    }
                                }

                        schema['data'].append(hashTemp)
                    else:
                        raise Exception('"values_list" precisa ser corretamente definido se multi_mod=True')
                
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.PATCH(url, headers=headers, json=schema)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.parent.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')

        def PATCHSchedule(self, task_id: str, frequency: Literal["once", "hourly", "daily", "weekly", "monthly"], 
                            interval: int = 1, starts_at: str = None, timezone: str = None, days: List[Union[int,str]]= None) -> dict:
            """
            Atualiza o agendamento de uma tarefa.

            #### Referência: 
            https://docs-apis.highbond.com/#operation/PATCHSchedule

            #### Parâmetros:
            - task_id (str): o id da tarefa
            - frequency (str): frequência de execução do agendamento, pode ser:
                - once: Define que o agendamento só será executado uma vez
                - hourly: Define uma frequência horária (depende do intervalo)
                - daily: Define uma frequência diária (depende do intervalo)
                - weekly: Define uma frequência semanal (depende do intervalo)
                - monthly: Define uma frequência mensal (depende do intervalo)
            - interval (int): o intervalo de tempo, a unidade muda com a frequência escolhida:
                - once: Não é definido
                - hourly: define o intervalo em minutos
                - daily: define o intervalo em dias
                - weekly: define o intervalo em semanas
                - monthly: define o intervalo em meses
            - starts_at (str): datahora da primeira execução do agendamento (yyyy-mm-dd THH:MM:SS.sssZ)
            - timezone (str): fusohorário da hora definida, (America/Sao_Paulo, conforme Ref.: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
            - days (list of integers or strings): define diferentes intervalos de execução para cada frequência, exceto por "once", "hourly" e "daily"
                - weekly: em quais dias da semana o agendamento será executado, sendo 0 domingo e 6 sábado, a lista pode ter 1 ou mais dias
                - monthly: em quais dias do mês o agendamento será executado, os dias podem ser definidos entre 1 e 28. Ou "last_day" para o último dia do mês, a lista só pode ter um valor

            #### Retorna:
            Um dicionário contendo informações sobre os agendamentos da tarefa

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            instance.PATCHSchedule('67336','daily', 2, starts_at='2024-02-17T22:00:00Z',timezone='America/Sao_Paulo')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Accept': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            frequencyNullCheckList = ['once', 'hourly', 'daily']

            if frequency in frequencyNullCheckList:
                hashDays = {}
            else:
                hashDays = {'days': days}

            schema = {
                "data": {
                    "type": "schedule",
                    "attributes": {
                        "frequency": frequency,
                        "interval": interval,
                        "starts_at": starts_at,
                        "starts_at_timezone": timezone,
                        "settings": hashDays
                    }
                }
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/schedule'

            # AÇÃO E RESPOSTA
            try:
                if frequency == "once":
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval != 1:
                        raise Exception('O intervalo não pode ser diferente de 1 para essa frequência')
                    
                elif frequency == 'hourly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em horas para essa frequência!')
                    
                elif frequency == 'daily':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fusohorário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')
                
                elif frequency == 'weekly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')

                    for day in days:
                        if not 0 <= day <= 6:
                            raise Exception('O parâmetro "days" não foi definido corretamente')
                
                elif frequency == 'monthly':
                    if starts_at == None:
                        raise Exception('É preciso definir corretamente a data da execução para eseta frequência!')
                    if timezone == None:
                        raise Exception('É preciso definir corretamente o fuso-horário!')
                    if interval <= 0:
                        raise Exception('É preciso definir um intervalo em dias para essa frequência!')

                    if len(days) == 1:
                        for day in days:
                            if isinstance(day, str):
                                if not day == "last_day":
                                    raise Exception('O parâmetro "days" não foi definido corretamente')
                            else:
                                if not 1 <= day <= 28:
                                    raise Exception('O parâmetro "days" não foi definido corretamente')
                    else:
                        raise Exception('Para esta frequência, o parâmetro "days" não pode ter mais de 1 item')
                    
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.PATCH(url, headers=headers, json=schema)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.parent.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')

        # === DELETE ===
        def deleteSchedule(self, task_id: str):
            """
            Deleta o agendamento de uma tarefa

            #### Referência:
            https://docs-apis.highbond.com/#operation/deleteRobotTask

            #### Parâmetros:
            - task_id (str): Id da tarefa

            #### Retorna:
            Um dict com informações sobre o agendamento deletado.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.deleteRobotTask('12345')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}/schedule'

            # AÇÃO E RESPOSTA
            try:
                
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.delete(url, headers=headers)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.parent.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')

        def deleteRobotJobs(self, job_id: str):
            """
            Deleta um registro de execução do robô

            #### Referência:
            https://docs-apis.highbond.com/#operation/deleteRobotJobs

            #### Parâmetros:
            - job_id (str): Id do registro de execução

            #### Retorna:
            Um dict com informações sobre o registro de execução deletado

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.deleteRobotJobs('12345')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/jobs/{job_id}'

            # AÇÃO E RESPOSTA
            try:
                
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')
                Response = rq.delete(url, headers=headers)

                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception(f'Código: 401\nMensagem: Falha na autenticação com self.parent.token -> {Response.json()}')
                elif Response.status_code == 403:
                    raise Exception(f'Código: 403\nMensagem: Conexão não permitida pelo servidor -> {Response.json()}')
                elif Response.status_code == 404:
                    raise Exception(f'Código: 404\nMensagem: Recurso não encontrado no API -> {Response.json()}')
                elif Response.status_code == 415:
                    raise Exception(f'Código: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição -> {Response.json()}')
                elif Response.status_code == 422:
                    raise Exception(f'Código: 422\nMensagem: Entidade improcessável -> {Response.json()}')
                elif Response.status_code == 200:
                    # A PROPRIEDADE Talkative CONTROLA SE AS MENSAGENS 
                    # DE SUCESSO VÃO FICAR SAINDO TODA VEZ QUE O MÉTODO RODA
                    if self.parent.talkative == True:
                        print('Código: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')

        def deleteRobotFile(self, file_id: str) -> dict:
            """
            Deleta um arquivo de um robô ACL

            #### Referência:
            - https://docs-apis.highbond.com/#operation/createRobotFile
            
            #### Parâmetros:
            - file_id (str): O ID do arquivo dentro do robô ACL a ser deletado.

            #### Retorna:
            Um dicionário contendo informações sobre o status da deleção.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='sua_organizacao')
            result = instance.deleteRobotFile(file_id='123')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo informações sobre o status da deleção.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_files/{file_id}'

            try:
                if self.parent.talkative == True:
                    print('Iniciando a requisição HTTP...')
                    
                Response = rq.delete(url, headers=headers)
                
                if Response.status_code == 400:
                    raise Exception(f'Código: 400\nMensagem: Falha na requisição API - > {Response.json()}')
                elif Response.status_code == 401:
                    raise Exception('\nCódigo: 401\nMensagem: Falha na autenticação com self.parent.token')
                elif Response.status_code == 403:
                    raise Exception('\nCódigo: 403\nMensagem: Conexão não permitida pelo servidor')
                elif Response.status_code == 404:
                    raise Exception('\nCódigo: 404\nMensagem: Recurso não encontrado no API')
                elif Response.status_code == 415:
                    raise Exception('\nCódigo: 415\nMensagem: Tipo de dado não suportado pelo API, altere o Content-Type no cabeçalho da requisição')
                elif Response.status_code == 200:
                    if self.parent.talkative == True:
                        print('\nCódigo: 200\nMensagem: Requisição executada com sucesso\n')
                        # SAÍDA COM SUCESSO
                        
                        return Response.json()
                    else:
                        return Response.json()
                else:
                    raise Exception(Response.json())

            except Exception as e:
                print(f'A requisição não foi possível:\n{e}')
    
        def deleteRobot(self, robot_id: str) -> dict:
            """
            Deleta um robô e todas as tarefas associadas a ele

            #### Referência:
            https://docs-apis.highbond.com/#operation/deleteRobot

            #### Parâmetros:
            - robot_id (str): O ID do robô que será deletado.
            
            #### Retorna:
            Um dicionário contendo informações sobre o robô deletado.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.deleteRobot('12345')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robots/{robot_id}'

            return self.parent.delete_command(api_url=url, api_headers=headers)

        def deleteRobotTask(self, task_id: str) -> dict:
            """
            Deleta uma tarefa de um robô do Highbond

            #### Referência:
            https://docs-apis.highbond.com/#operation/deleteRobotTask

            #### Parâmetros:
            - task_id (str): Id da tarefa que será deletada

            #### Retorna:
            Um dict com informações sobre a tarefa deletada.

            #### Exceções:
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi('seu_self.parent.token', 'sua_organização')
            instance.deleteRobotTask('12345')
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/robot_tasks/{task_id}'

            return self.parent.delete_command(api_url=url, api_headers=headers)

    class _Strategy():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
        def getStrategyRisks(self, 
                                fields: str = 'title,description,status,score,residual_score,heat,residual_heat,strategy_custom_attributes,risk_manager_risk_id,created_at,updated_at', 
                                page_size: int = 100, 
                                page: int = 1) -> dict:
            """
            Lista os arquivos relacionados a um robô ACL em um ambiente específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getStrategyRisks

            #### Parâmetros:
            
            """
            
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[strategy_risks]': fields,
                'page[size]' : page_size,
                'page[number]': base64.encodebytes(str(page).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/strategy_risks'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getStrategySegments(self, 
                                page_size: int = 100, 
                                page: int = 1) -> dict:
            """
            Lista os arquivos relacionados a um robô ACL em um ambiente específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getStrategySegments
            
            #### Parâmetros:

            """
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'page[size]' : page_size,
                'page[number]': base64.encodebytes(str(page).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/strategy_segments'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getStrategyRiskSegments(self, strategy_risk_id: str, page_size: int = 100, page: int = 1) -> dict:
            """
            Retrieves the full list of the risks's operating segments from Strategy.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getStrategyRiskSegments

            #### Parâmetros:
            - strategy_risk_id: id do risco estratégico a ser consultado
            - page_size: quantidade de registros nesta consulta
            - page: página consultada

            #### Retorna:
            Um dicionário contendo informações sobre o risco estratégico consultado

            #### Exceções:
            - Sobe exceção se o ambiente não estiver definido corretamente.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            instance = hbapi(self.parent.token='seu_self.parent.token', organization_id='id_da_organização')
            result = instance.getStrategyRiskSegments(strategy_risk_id='45323', page_size=10, page=1)
            ```

            #### Observações:
            - Certifique-se de que a propriedade 'talkative' esteja configurada corretamente para controlar as mensagens de sucesso.
            - A resposta é um dicionário contendo as informações sobre os arquivos do robô.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            params = {
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/strategy_risks/{strategy_risk_id}/strategy_segments'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getStrategyRiskSegment(self, 
                                    strategy_risk_id: str, 
                                    segment_id: str,
                                    segment_fields: str = 'name,score,strategy_factors,created_at,updated_at', 
                                    factors_fields: str = 'id,treatment_value,treatment_weight,treatment_factors,severity_value'
                                    ) -> dict:
            """
            Get information about an operating segment for the risk.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getStrategyRiskSegment

            #### Parâmetros:
            
            
            """
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            if factors_fields == '':
                factors_fields = None
            
            if segment_fields == '':
                raise Exception('O método não pode ser chamado sem um campo de consulta')

            params = {
                'fields[strategy_segments]': segment_fields,
                'fields[strategy_factors]': factors_fields
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/strategy_risks/{strategy_risk_id}/strategy_segments/{segment_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)

        def getStrategyObjectives(self, page_size: int = 100, page_num: int = 1) -> dict:
            """
            Retorna todos os objetivos estratégicos da organização.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getStrategyObjectives

            #### Parâmetros:
            - page_size: parâmetro que define a quantidade de registros retornados
            
            """
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'page[size]': page_size,
                'page[number]': base64.encodebytes(str(page_num).encode()).decode()
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/strategy_objectives'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===
 
    class _ToDos():
        def __init__(self, parent):
            self.parent = parent
            
        # === GET ===
        def getToDos(self,
                id: str = '',
                fields: list = ['description','project','due_date','status',
                                'created_at','updated_at','assigned_to','creator','target'],
                project_id: str = None,
                project_state: str = None,
                target_id: str = None,
                target_type: Literal["projects", "controls", "control_tests", "control_test_plans",
                                    "issues", "narratives", "objectives", "walkthrough_summaries",
                                    "project_files", "project_plannings", "project_results", "risks",
                                    "risk_control_matrices", "testing_rounds", "walkthroughs"] = None,
                sort: Literal['id','status','created_at','-id','-status','-created_at'] = 'id',
                include: Literal['assigned_to','target','creator'] = None,
                page_num: int = 1,
                page_size: int = 100
                ) -> dict:
            """
            Consulta todos os to_dos da organização ou um em específico.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getOrgProjectsTodos\n
            https://docs-apis.highbond.com/#operation/getTodo

            #### Parâmetros:

            #### Retorna:

            #### Exceções:
            - Sobe exceção se o id da organização não for encontrado.
            - Sobe exceção se a requisição API falhar com códigos de status diferentes de 200.
            - Sobe exceção se houver uma falha desconhecida.

            #### Exemplo de uso:
            ```python
            ```

            #### Observações:
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }
            
            params = {
                "fields[projects_todos]": ",".join(fields),
                "filter[project.id]": project_id,
                "filter[project.state]": project_state,
                "filter[target.id]": target_id,
                "filter[target.type]": target_type,
                "sort": sort,
                "page[size]": page_size,
                "page[number]": base64.b64encode(str(page_num).encode()).decode(),
                "include": {",".join(include) if include else include}
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/projects_todos/{id}'
            
            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===
    
    class _Users():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
        def getUsers(self, uid: str = '') -> dict:
            """
            Retorna todos ou um usuário caso seja passado o `id`
            
            #### Referência:
            https://docs-apis.highbond.com/public.html#operation/getUsers
            
            """
            
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/users/{uid}'

            return self.parent.get_command(api_url=url, api_headers=headers)
        
        # === POST ===
            
        # === PATCH ===
        
        # === DELETE ===

    class _Walkthroughs():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
            
        def getOrganizationWalkthroughs(self,
                            fields: list = ['walkthrough_results', 'control_design', 'created_at', 'updated_at', 'custom_attributes',
                                            'control', 'planned_milestone_date', 'actual_milestone_date'],
                            sort: Literal["id", "walkthrough_results","control_design", "created_at", "updated_at"] = "id",
                            project_id: str = None,
                            project_name: str = None,
                            project_state: str = "active",
                            project_status: str = None,
                            control_id: list = None,
                            control_design: Literal["true", "false", ""] = None,
                            control_title: str = None,
                            control_id_interno: list = None,
                            control_query: str = None,
                            control_status: str = None,
                            control_owner: str = None,
                            control_frequency: str = None,
                            control_type: str = None,
                            objective_title: str = None,
                            objective_reference: str = None,
                            test_round_1_user_id: str = None,
                            test_round_2_user_id: str = None,
                            test_round_3_user_id: str = None,
                            test_round_4_user_id: str = None,
                            include: list = ["control","control.objective"],
                            fields_controls: list = ["title","description","control_id","owner","frequency","control_type","prevent_detect","method","status","position", "created_at","updated_at","custom_attributes","objective","walkthrough","control_test_plan","control_tests","mitigations","owner_user","entities","framework_origin"],
                            fields_objectives: List[Literal["title","description","reference","division_department","owner","executive_owner","created_at","updated_at","project","assigned_user","custom_attributes","position","risk_control_matrix_id","walkthrough_summary_id","testing_round_1_id","testing_round_2_id","testing_round_3_id","testing_round_4_id","entities","framework","framework_origin","risk_assurance_data","planned_start_date","actual_start_date","planned_end_date","actual_end_date","planned_milestone_date","actual_milestone_date"]] = ["title","description","reference","division_department","owner","executive_owner","created_at","updated_at"],
                            page_size: int = 100,
                            page_num: int = 1) -> dict:
            """
            Consulta Walkthroughs da organização com base em filtros avançados por projeto, controle, objetivo, responsáveis e status.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getOrganizationWalkthroughs

            #### Parâmetros:

            - **fields** (`list`): Lista de campos a serem retornados.  
            *Exemplo:* `['walkthrough_results','control_design','created_at']`

            - **sort** (`str`): Campo de ordenação (ascendente ou descendente com `-`).  
            *Opções:* `"id"`, `"walkthrough_results"`, `"control_design"`, `"created_at"`, `"updated_at"`  
            *Exemplo:* `"id"` ou `"-created_at"`

            ##### Filtros de projeto:
            - **project_id** (`str`): Filtra por ID do projeto.  
            *Exemplo:* `"123"`
            - **project_name** (`str`): Filtra por nome do projeto.  
            *Exemplo:* `"Projeto X"`
            - **project_state** (`str`): Filtra por estado do projeto.  
            *Exemplo:* `"active"`
            - **project_status** (`str`): Filtra por status do projeto.  
            *Exemplo:* `"active"`

            ##### Filtros de controle:
            - **control_id** (`list`): Filtra por IDs do controle.  
            *Exemplo:* `["1", "2", "3"]`
            - **control_design** (`str`): Filtra por walkthroughs com controle adequadamente desenhado.  
            *Valores:* `"true"`, `"false"`
            - **control_title** (`str`): Filtra pelo título do controle.  
            - **control_id_interno** (`list`): Filtra por IDs internos (`control.control_id`).  
            *Exemplo:* `["001", "002"]`
            - **control_query** (`str`): Busca textual no título ou descrição do controle.  
            - **control_status** (`str`): Filtra pelo status do controle.  
            *Exemplo:* `"Key Control"`
            - **control_owner** (`str`): Filtra pelo proprietário do controle.  
            *Exemplo:* `"usuario@empresa.com"`
            - **control_frequency** (`str`): Filtra pela frequência do controle.  
            *Exemplo:* `"Monthly"`
            - **control_type** (`str`): Filtra pelo tipo do controle.  
            *Exemplo:* `"Application/System Control"`

            ##### Filtros de objetivo:
            - **objective_title** (`str`): Filtra pelo título do objetivo.  
            - **objective_reference** (`str`): Filtra pela referência do objetivo.  

            ##### Filtros de responsáveis por testes:
            - **test_round_1_user_id** (`str`): Filtra por usuário atribuído ao 1º round.  
            - **test_round_2_user_id** (`str`): Filtra por usuário atribuído ao 2º round.  
            - **test_round_3_user_id** (`str`): Filtra por usuário atribuído ao 3º round.  
            - **test_round_4_user_id** (`str`): Filtra por usuário atribuído ao 4º round.  

            ##### Inclusão de entidades relacionadas:
            - **include** (`str`): Define entidades relacionadas para inclusão.  
            *Exemplo:* `"control,control.objective"`
            - **fields_controls** (`str`): Campos a retornar da entidade `controls`.  
            *Exemplo:* `"title,control_id,owner,status"`
            - **fields_objectives** (`str`): Campos a retornar da entidade `objectives`.  
            *Exemplo:* `"title,reference,owner"`

            ##### Paginação:
            - **page_size** (`int`): Número de itens por página (padrão: 100, máx: 100).  
            - **page_num** (`int`): Número da página (codificado em Base64 internamente).  

            #### Retorno:
            - `dict`: Dicionário com os walkthroughs encontrados conforme os filtros aplicados.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver configurado corretamente (`self.parent.token`, `organization_id`, `self.parent.server`).
            - Sobe exceção se a requisição retornar código HTTP diferente de `200`.
            - Sobe exceção para falhas inesperadas ou erros internos da API.

            #### Exemplo de uso:
            ```python
            api = hbapi(token="seu_token", organization_id="self.parent.organization_id")
            walkthroughs = api.getOrganizationWalkthroughs(
                project_id="123",
                control_status="Key Control",
                sort="-created_at",
                page_size=50
            )
            ```
            
            #### Observações:
            - Os filtros do tipo lista (ex: `control_id`, `control_id_interno`) são convertidos para string separada por vírgula conforme esperado pela API.
            - O número da página é automaticamente codificado em Base64 para atender ao padrão exigido pela API (`page[number]`).
            - O campo `sort` aceita apenas um valor por vez e deve ser utilizado com cautela para garantir performance.
            - Os campos `fields[controls]` e `fields[objectives]` devem conter apenas atributos válidos das respectivas entidades.
            - O uso do parâmetro `include` pode impactar o tempo de resposta da API, dependendo da profundidade das relações requisitadas.
            - Certifique-se de que os valores utilizados nos filtros correspondem exatamente aos valores esperados pela base de dados da API (case-sensitive, enum etc.).
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[walkthroughs]': ','.join(fields) if fields else fields,
                'sort': sort,
                'filter[project.id]': project_id,
                'filter[project.name]': project_name,
                'filter[project.state]': project_state,
                'filter[project.status]': project_status,
                'filter[control.id]': ','.join(control_id) if control_id else control_id,
                'filter[control_design]': control_design,
                'filter[control.title]': control_title,
                'filter[control.control_id]': ','.join(control_id_interno) if control_id_interno else control_id_interno,
                'filter[control.query]': control_query,
                'filter[control.status]': control_status,
                'filter[control.owner]': control_owner,
                'filter[control.frequency]': control_frequency,
                'filter[control.control_type]': control_type,
                'filter[objective.title]': objective_title,
                'filter[objective.reference]': objective_reference,
                'filter[control.control_tests.1.assigned_user.id]': test_round_1_user_id,
                'filter[control.control_tests.2.assigned_user.id]': test_round_2_user_id,
                'filter[control.control_tests.3.assigned_user.id]': test_round_3_user_id,
                'filter[control.control_tests.4.assigned_user.id]': test_round_4_user_id,
                'include': ','.join(include) if include else include,
                'fields[controls]': ','.join(fields_controls) if fields_controls else fields_controls,
                'fields[objectives]': ','.join(fields_objectives) if fields_controls else fields_controls,
                'page[size]': str(page_size),
                'page[number]': base64.b64encode(str(page_num).encode()).decode(),
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/walkthroughs'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
    
        def getWalkthrough(self,
                            walkthrough_id: str,
                            fields: List[Literal['walkthrough_results', 'control_design', 'created_at', 'updated_at', 'custom_attributes',
                                            'control', 'planned_milestone_date', 'actual_milestone_date']] 
                                            = 
                                            ['walkthrough_results', 'control_design', 'created_at', 'updated_at', 'custom_attributes',
                                            'control', 'planned_milestone_date', 'actual_milestone_date'],
                            include: List[Literal["control","control.objective", None]] = ["control","control.objective"]
            ) -> dict:
            """
            Consulta Walkthroughs da organização com base em filtros avançados por projeto, controle, objetivo, responsáveis e status.

            #### Referência:
            https://docs-apis.highbond.com/#operation/getWalkthrough

            #### Parâmetros:

            - **fields** (`list`): Lista de campos a serem retornados.  
            *Exemplo:* `['walkthrough_results','control_design','created_at']` 

            ##### Inclusão de entidades relacionadas:
            - **include** (`str`): Define entidades relacionadas para inclusão.  
            *Exemplo:* `"control,control.objective"`

            #### Retorno:
            - `dict`: Dicionário dados de um walkthrough específico.

            #### Exceções:
            - Sobe exceção se o ambiente não estiver configurado corretamente (`self.parent.token`, `organization_id`, `self.parent.server`).
            - Sobe exceção se a requisição retornar código HTTP diferente de `200`.
            - Sobe exceção para falhas inesperadas ou erros internos da API.

            #### Exemplo de uso:
            ```python
            api = hbapi(token="seu_token", organization_id="self.parent.organization_id")
            walkthroughs = api.getWalkthrough(
                walkthrough_id="1234",
            )
            ```
            
            #### Observações:
            - Os paramêtros do tipo lista (ex: `fields`, `include`) são convertidos para string separada por vírgula conforme esperado pela API.
            - O uso do parâmetro `include` pode impactar o tempo de resposta da API, dependendo da profundidade das relações requisitadas.
            """
            headers = {
                'Content-type': 'application/vnd.api+json',
                'Authorization': f'Bearer {self.parent.token}'
            }

            params = {
                'fields[walkthroughs]': ','.join(fields) if fields else fields,
                'include': ','.join(include) if include else include,
            }

            url = f'{self.parent.protocol}://{self.parent.server}/v1/orgs/{self.parent.organization_id}/walkthroughs/{walkthrough_id}'

            return self.parent.get_command(api_url=url, api_headers=headers, api_params=params)
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===

    #modelo:
    class exemplo():
        def __init__(self, parent):
            self.parent = parent
        
        # === GET ===
        
        # === POST ===
        
        # === PATCH ===
        
        # === DELETE ===