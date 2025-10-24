# file_manager.py
import os
import json

class QuizFileManager:
    """퀴즈 데이터 파일을 관리하는 클래스"""
    KEY = "quiz"
    def __init__(self, file_path):
        self.file_path = file_path
        
    def load_file(self):
        """파일에서 퀴즈 데이터를 불러옵니다."""
        if not os.path.exists(self.file_path): # 파일이 없으면 빈 리스트 반환
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
            return file_data.get(self.KEY, []) # KEY가 없는 경우에도 빈 리스트 반환
        except json.JSONDecodeError: # JSON 파일 형식이 잘못되었을 경우
            print(f"경고: '{self.file_path}' 파일이 올바른 JSON 형식이 아닙니다. 빈 퀴즈 목록을 로드합니다.")
            return []
        except Exception as e:
            print(f"파일 로드 중 오류 발생: {e}")
            return []

    def save_file(self, file_data):
        """퀴즈 데이터를 파일에 저장합니다."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({self.KEY: file_data}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")


class LastFailedFileManager(QuizFileManager):
    """최근 틀린 문제 파일을 관리하는 클래스"""
    KEY = "last_failed"
    def __init__(self, file_path):
        super().__init__(file_path)
