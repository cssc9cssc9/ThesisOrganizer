import os , sys, datetime, shutil, json, re
from utils.DAO import SemanticScholarTool, PaperProcessor
from component.paper_info import PaperInfo
class PaperRegister:
    def __init__(self):
        self.semantic_tool = SemanticScholarTool()
        pass

    def RegisterWithPapersFolder(self, source_dir, target_dir:str=None):
        file_names:list[str] = [file for file in os.listdir(source_dir) if file.endswith('.pdf')]
        identify_ids:list[str] = [file_name.rsplit('.pdf', 1)[0] for file_name in file_names]
        paper_infos = self.semantic_tool.GetPapersWithListPaperId(identify_ids)
        if target_dir is None:
            target_dir = source_dir
        for file_name in file_names:
            identify_id = file_name.rsplit('.pdf', 1)[0]
            if identify_id in paper_infos:
                paper_info:PaperInfo = paper_infos[identify_id]
                paper_data = paper_info.get_data()
                processor = PaperProcessor(paper_info)
                publication_date = datetime.datetime.strptime(paper_data['publicationDate'], "%Y-%m-%d").strftime('%Y%m%d') if paper_data['publicationDate'] else "Null"
                paper_title = paper_data['title'].replace("?", "").replace(":", "")
                folder_name = os.path.join(target_dir, f"{publication_date} {paper_title}")
                os.makedirs(folder_name, exist_ok=True)
                processor.CreateNewPaperFolder(os.path.join(source_dir, file_name), folder_name)
        
    
    def RegisterWithPaperId(self, paper_path:str, target_dir:str):
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if file_name.endswith('.pdf'):
            identify_id = file_name.replace(".pdf", "")
            paper_id = self.__AssignPaperId(identify_id)
            paper_info = self.semantic_tool.GetPaperFromPaperId(paper_id)
            processor = PaperProcessor(paper_info)
            paper_data = paper_info.get_data()
            publication_date = datetime.datetime.strptime(paper_data['publicationDate'], "%Y-%m-%d").strftime('%Y%m%d') if paper_data['publicationDate'] else "Null"
            paper_title = paper_data['title'].replace("?", "").replace(":", "")
            target_folder_name = os.path.join(target_dir, f"{publication_date} {paper_title}")
            os.makedirs(target_folder_name, exist_ok=True)
            processor.CreateNewPaperFolder(os.path.join(paper_path), target_folder_name)

    def CleanPapersFolder(self, target_dir, delete_related_folder=False):
        folders:list = os.listdir(target_dir)
        if os.path.exists(os.path.join(target_dir, ".temp")):
            folders.pop(".temp")
        else:
            os.makedirs(os.path.join(target_dir, ".temp"))
        temp_dir = os.path.join(target_dir, ".temp")
        for folder in folders:
            folder_path = os.path.join(target_dir, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(".pdf"):
                        paper_path = os.path.join(folder_path, file)
                        os.rename(paper_path, os.path.join(temp_dir, file))
                if delete_related_folder:
                    shutil.rmtree(folder_path)
            
    def UpdatePaperInformation(self, target_dir:str):
        if os.path.isdir(target_dir):
            paper_dir = target_dir
        else:
            paper_dir = os.path.dirname(target_dir)
        if 'config.json' in os.listdir(paper_dir):
            with open(os.path.join(paper_dir, 'config.json'), 'r') as fp:
                paper_config =  json.load(fp)
            try:
                if os.path.dirname(paper_config['location']) != target_dir:
                    identify_id = paper_config['identifyId']
                    paper_path = os.path.join(target_dir, f"{identify_id}.pdf")
                    if not os.path.exists(paper_path):
                        raise FileNotFoundError('Wrong folder format.')
                    self.RegisterWithPaperId(paper_path, os.path.dirname(target_dir))
            except KeyError as key_e:
                print(f"The format in [{paper_dir}]'s config is wrong")
                for file_name in os.listdir(target_dir):
                    if os.path.join(target_dir, file_name).endswith('.pdf'):
                        self.RegisterWithPaperId(os.path.join(target_dir, file_name), os.path.dirname(target_dir))
        else:
            for file_name in os.listdir(target_dir):
                if os.path.join(target_dir, file_name).endswith('.pdf'):
                    self.RegisterWithPaperId(os.path.join(target_dir, file_name), os.path.dirname(target_dir))
    
    def UpdatePaperinformationInFolder(self, papers_folder:str):
        for folder in os.listdir(papers_folder):
            if os.path.isdir(os.path.join(papers_folder, folder)):
                paper_folder = os.path.join(papers_folder, folder)
                self.UpdatePaperInformation(paper_folder)
            

    def __AssignPaperId(self, identifyId):
        if len(identifyId)<11:
            paper_id = f"ArXiv:{identifyId}"
        else:
            paper_id = identifyId
        return paper_id 