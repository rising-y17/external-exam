# ui.py
import os
import platform

class QuizUI:
    """콘솔 기반 사용자 인터페이스를 관리하는 클래스"""
    def __init__(self):
        self.clear_cmd = "cls" if platform.system() == "Windows" else "clear"

    def show_menu(self):
        """메인 메뉴를 화면에 표시합니다."""
        self.clear() 
        print("\n" + "="*30)
        print("        파이썬 퀴즈 앱")
        print("="*30)
        print("1. 모든 문제 풀어보기")
        print("2. 최근에 틀린 문제 풀어보기")
        print("3. 이전에 틀렸던 문제 다시 풀어보기 (많이 틀린 것 우선)")
        print("4. 문제 추가하기")
        print("5. 문답 전체 마크다운으로 출력하기")
        print("6. 마지막으로 풀은 문제 답안 정답 처리")
        print("0. 종료")
        print("="*30)

    def get_menu_choice(self):
        """사용자로부터 메뉴 선택을 입력받습니다."""
        while True:
            try:
                choice = input("원하시는 메뉴를 선택하세요: ")
                if choice in ['1', '2', '3', '4', '5', '6', '0']:
                    return choice
                else:
                    print("유효하지 않은 번호입니다. 다시 입력해주세요.")
            except EOFError:
                print("\n프로그램을 종료합니다.")
                return '0'

    def clear(self):
        """콘솔 화면을 지웁니다."""
        os.system(self.clear_cmd)
        
    def wait_for_enter(self):
        """사용자가 엔터를 누를 때까지 기다립니다."""
        input("\n메뉴로 돌아가려면 엔터를 누르세요...")

