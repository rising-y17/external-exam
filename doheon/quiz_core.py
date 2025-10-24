# quiz_core.py
import random
from file_manager import QuizFileManager, LastFailedFileManager
from ui import QuizUI
from quiz_parser import QuizParser

class QuizApp:
    """퀴즈 애플리케이션의 핵심 로직을 담당하는 클래스"""
    def __init__(self,
                 quiz_file="quiz.json",
                 wrong_note_file="wrong_quiz_note.md",
                 last_failed_file="last_failed.json"):
        self.quiz_file_manager = QuizFileManager(quiz_file)
        self.last_failed_file_manager = LastFailedFileManager(last_failed_file)
        self.ui = QuizUI()
        self.parser = QuizParser()
        
        self.quiz_data = self.quiz_file_manager.load_file()
        self.wrong_note_file = wrong_note_file
        
        self.last_user_answer = None
        self.last_question = None
        self.last_failed = []

    def _save_one_item(self, question_text: str, answers: list, hint: str):
        """하나의 퀴즈 아이템을 저장하거나 업데이트합니다."""
        if not question_text or not answers:
            return "본문 또는 정답 없음 → 건너뜀"

        existing = next((item for item in self.quiz_data if item.get("question", "").strip() == question_text), None)

        if existing:
            to_add = [a for a in answers if a not in existing.get("answers", [])]
            if to_add:
                existing["answers"].extend(to_add)
                if hint: existing["hint"] = hint
                self.quiz_file_manager.save_file(self.quiz_data)
                return f"• 기존 문제에 정답 추가: {to_add}"
            return "• 중복(변경 없음)"
        else:
            new_item = {"question": question_text, "answers": answers, "wrong_count": 0}
            if hint:
                new_item["hint"] = hint
            self.quiz_data.append(new_item)
            self.quiz_file_manager.save_file(self.quiz_data)
            return "• 새 문제 저장"

    def decrease_wrong_count(self, q_item):
        """문제의 오답 횟수를 1 감소시킵니다."""
        if q_item["wrong_count"] > 0:
            q_item["wrong_count"] -= 1
            print(f"오답 횟수 1 감소. 현재 오답 횟수: {q_item['wrong_count']}")
        else:
            print("오답 횟수가 이미 0입니다.")
        self.quiz_file_manager.save_file(self.quiz_data)

    def handle_command(self, cmd: str, q_item: dict):
        """퀴즈 풀이 중 입력된 명령어를 처리합니다."""
        if cmd in ('quit', '종료'):
            print("\n퀴즈 풀이를 종료합니다.")
            return True, False
            
        elif cmd in ('add', '추가') and self.last_user_answer and self.last_question:
            if self.last_user_answer not in self.last_question["answers"]:
                self.last_question["answers"].append(self.last_user_answer)
                print("이전 답안이 정답으로 추가되었습니다.")
                self.decrease_wrong_count(self.last_question)
                self.last_user_answer = None
                return False, True
            print("이미 등록된 정답입니다.")
        
        elif cmd in ('typo', '오타') and self.last_user_answer and self.last_question:
            print("오타로 처리하여 오답 횟수를 조정합니다.")
            self.decrease_wrong_count(self.last_question)
            self.last_user_answer = None
            return False, True
        
        elif cmd in ('hint', '힌트'):
            hint = q_item.get("hint")
            print(f"힌트: {hint}" if hint else "이 문제에는 힌트가 없습니다.")
        
        else:
            print("알 수 없는 명령이거나, 명령을 처리할 수 없는 상태입니다.")
        return False, False
    
    def ask_single_question(self, q_item):
        """하나의 문제를 출제하고 사용자의 답변을 처리합니다."""
        print(q_item["question"])
        bonus = 0

        while True:
            user_input = input("정답을 입력하세요: ").strip()

            if user_input.startswith('!'):
                should_quit, prev_fixed = self.handle_command(user_input[1:].lower(), q_item)
                if should_quit: return bonus, True
                if prev_fixed:
                    bonus += 1
                    if self.last_failed: self.last_failed.pop()
                continue

            self.last_user_answer = user_input
            if user_input in q_item["answers"]:
                print("정답입니다!")
                return bonus + 1, False

            print(f"틀렸습니다. 정답: {' || '.join(q_item['answers'])}")
            q_item["wrong_count"] += 1
            if q_item not in self.last_failed:
                self.last_failed.append(q_item)
            return bonus, False

    def play_quizzes(self, q_data: list, quiz_type="모든"):
        """주어진 퀴즈 데이터로 퀴즈를 진행합니다."""
        if not q_data:
            print(f"{quiz_type} 퀴즈 데이터가 없습니다.")
            return
        
        self.last_failed = []
        random.shuffle(q_data)

        print(f"\n--- {quiz_type} 문제 풀어보기 시작 ---")
        print("  - 특수 명령: !quit, !add, !typo, !hint")
        print("------------------------------")
        
        score, attempted = 0, 0
        quiz_list = list(q_data)

        for i, q_item in enumerate(quiz_list):
            attempted += 1
            print(f"\n--- 문제 {i + 1}/{len(quiz_list)} ---")
            
            correct_count, should_quit = self.ask_single_question(q_item)
            score += correct_count
            self.quiz_file_manager.save_file(self.quiz_data)
            
            if should_quit:
                attempted -= 1
                break
            
            self.last_question = q_item
            
        print("\n--- 퀴즈 풀이 결과 ---")
        if attempted > 0:
            print(f"총 {attempted} 문제 중 {score} 문제 정답! ({score/attempted*100:.2f}%)")
        else:
            print("풀이한 문제가 없습니다.")

        self.last_failed_file_manager.save_file(self.last_failed)

    def play_all_quizzes(self):
        if not self.quiz_data:
            print("등록된 퀴즈가 없습니다. 먼저 문제를 추가해주세요.")
            return
        self.play_quizzes(self.quiz_data, quiz_type="모든")

    def play_last_failed(self):
        last_failed_data = self.last_failed_file_manager.load_file()
        if not last_failed_data:
            print("최근에 틀린 문제가 없습니다.")
            return
        self.play_quizzes(last_failed_data, quiz_type="최근에 틀린")

    def play_all_failed(self):
        failed_list = self.get_failed_quizzes()
        if failed_list:
            self.play_quizzes(failed_list, quiz_type="틀렸던 모든")

    def correct_last_question(self):
        if not self.last_user_answer or not self.last_question:
            print("정답 처리할 최근 답변이 없습니다.")
            return
        
        choice = input(f"'{self.last_user_answer}'을(를) 정답에 추가할까요? (y: 정답 추가 / n: 단순 오타 처리): ").lower()
        if choice == 'y':
            self.handle_command("add", None)
        else:
            self.handle_command("typo", None)

    def add_quiz_interactive(self):
        """대화형으로 퀴즈를 추가하는 모드입니다."""
        print("\n--- [문제 추가 모드] ---")
        print("명령: :+ (저장), :* (종료), :$ (파일에서 불러오기)")
        
        question_lines, answers, hint = [], [], None

        while True:
            try:
                line = input("> ").rstrip("\n")
            except EOFError:
                print("\n입력이 중단되었습니다. 저장 없이 종료합니다.")
                return
            
            if line.startswith(":$"):
                self.add_quiz_from_file(line[2:].strip() or "new_quiz.txt")
                question_lines, answers, hint = [], [], None
                continue

            elif line.startswith(":+"):
                question_text = "\n".join(question_lines).strip()
                result = self._save_one_item(question_text, answers, hint)
                print(f"\n[알림] {result}")
                question_lines, answers, hint = [], [], None
                continue

            elif line.startswith(":*"):
                print("\n문제 추가 모드를 종료합니다.")
                return

            elif line.startswith(":="):
                raw = line[2:].strip()
                answers = [a.strip() for a in raw.split("||") if a.strip()]
                print(f"(정답 설정) {answers}")

            # ... 기타 명령어 처리 ...

            else:
                question_lines.append(line)

    def add_quiz_from_file(self, path: str):
        """파일로부터 여러 퀴즈를 한 번에 추가합니다."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                full_text = f.read()
            
            blocks = self.parser.parse_file_into_blocks(full_text)
            print(f"\n[알림] '{path}'에서 {len(blocks)}개 블록 감지. 처리 중...")

            for idx, blk in enumerate(blocks, 1):
                q_text, ans, h = self.parser.parse_quiz_block(blk)
                if not q_text and not ans and not h: continue
                result = self._save_one_item(q_text, ans, h)
                print(f"[{idx:02d}] {result}")

        except FileNotFoundError:
            print(f"[오류] 파일을 찾을 수 없습니다: {path}")
        except Exception as e:
            print(f"[오류] 파일 처리 중 예외 발생: {e}")

    def get_failed_quizzes(self):
        """오답 횟수가 1 이상인 모든 퀴즈를 오답 횟수 순으로 정렬하여 반환합니다."""
        if not self.quiz_data:
            print("퀴즈 데이터가 없습니다.")
            return None
        
        items = sorted(
            (q for q in self.quiz_data if q.get("wrong_count", 0) >= 1),
            key=lambda x: x["wrong_count"],
            reverse=True
        )
        if not items:
            print("틀린 문제가 없습니다!")
            return None
        return items

    def export_wrong_note_markdown(self):
        """오답 노트를 마크다운 파일로 생성합니다."""
        items = self.get_failed_quizzes()
        if not items: return
        
        lines = ["# 오답노트\n"]
        for idx, q in enumerate(items, 1):
            lines.append(f"## {idx}. (오답 {q.get('wrong_count', 0)}회)")
            lines.append(f"**문제**\n\n```\n{q.get('question', '')}\n```")
            if q.get("hint"):
                lines.append(f"\n> 힌트: {q.get('hint')}")
            lines.append("\n**정답**\n")
            lines.extend([f"- {a}" for a in q.get("answers", [])])
            lines.append("\n---\n")

        try:
            with open(self.wrong_note_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"오답노트를 '{self.wrong_note_file}' 파일로 생성했습니다.")
        except Exception as e:
            print(f"오답노트 생성 중 오류 발생: {e}")

    def run(self):
        """애플리케이션의 메인 루프를 실행합니다."""
        menu_actions = {
            '1': self.play_all_quizzes,
            '2': self.play_last_failed,
            '3': self.play_all_failed,
            '4': self.add_quiz_interactive,
            '5': self.export_wrong_note_markdown,
            '6': self.correct_last_question,
        }
        
        while True:
            self.ui.show_menu()
            choice = self.ui.get_menu_choice()

            if choice == '0':
                print("\n퀴즈 앱을 종료합니다.")
                break
            
            action = menu_actions.get(choice)
            if action:
                action()
            
            self.ui.wait_for_enter()
