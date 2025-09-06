import os
import json
import random

def load_quiz(folder="quiz_list"):
    quiz_groups = {}
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            file_path = os.path.join(folder, filename)
            name, _ = os.path.splitext(filename)  # 확장자 제거
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if "quiz" in data and isinstance(data["quiz"], list):
                        quiz_groups[name] = data["quiz"]
                except json.JSONDecodeError as e:
                    print(f"{filename} 파일을 읽는 중 오류 발생: {e}")
    return quiz_groups


def select_quiz_group(quiz_groups):
    # 메뉴 출력
    keys = list(quiz_groups.keys())
    for i, name in enumerate(keys, start=1):
        print(f"{i}. {name}")
    print("a. 모두 풀어보기")

    while True:
        # 입력받기
        choice = input("선택: ").strip()

        if choice.lower() == "a":  # 모두 풀기
            all_quizzes = []
            for group in quiz_groups.values():
                all_quizzes.extend(group)
            return all_quizzes

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                return quiz_groups[keys[idx]]

        print("잘못된 입력입니다.")

def run_quiz(quiz_list):
    quiz_list = quiz_list[:]
    random.shuffle(quiz_list)
    total = len(quiz_list)
    asked = 0
    correct = 0

    for i, quiz in enumerate(quiz_list, start=1):
        print(f"\n--- 문제 {i}/{total} ---")
        print(quiz["question"])

        # 사용자 입력 받기
        user_answer = input("정답 입력: ").strip()

        # 정답 확인
        if user_answer.lower() in ["!종료", "!exit", "!quit"]:
            print("\n퀴즈를 종료합니다.")
            break

        if user_answer.lower() in [a.lower() for a in quiz["answers"]]:
            print("정답입니다!")
            correct += 1
        else:
            print("오답입니다.")
            print(f"정답: {' || '.join(quiz['answers'])}")
        asked += 1

    print("\n--- 결과 ---")
    if asked > 0:
        print(f"총 {asked}문제 중 {correct}문제 정답 ({correct/asked*100:.2f}%)")
    else:
        print("풀은 문제가 없습니다.")

if __name__ == "__main__":
    quizzes = load_quiz("quiz_list")
    selected = select_quiz_group(quizzes)
    run_quiz(selected)
