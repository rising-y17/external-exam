import json
import os

def make_quiz_dic():
    """
    new_quiz.txt 파일을 읽어 파이썬 딕셔너리 리스트로 변환합니다.
    """
    try:
        with open("new_quiz.txt", 'r', encoding='utf-8') as f:
            quiz_list = []
            quiz = {}
            question = ""
            for line in f:
                if line.startswith("== "):
                    if question:
                        answers = line[3:].strip().split("||")
                        quiz["answers"] = answers
                        quiz["question"] = question.strip()
                        quiz["wrong_count"] = 0
                        quiz_list.append(quiz)
                        quiz = {}
                        question = ""
                else:
                    question += line
    except FileNotFoundError:
        print("오류: 'new_quiz.txt' 파일을 찾을 수 없습니다.")
        return []
    return quiz_list

def save_or_update_quiz(name, new_quiz_data):
    """
    퀴즈 데이터를 JSON 파일로 저장하거나, 기존 파일에 병합합니다.
    """
    output_dir = "./quiz_list/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"'{output_dir}' 디렉토리를 생성했습니다.")

    file_path = os.path.join(output_dir, f"{name}.json")

    # 1. 파일이 이미 존재하는 경우, 데이터 병합 로직 수행
    if os.path.exists(file_path):
        print(f"'{file_path}' 파일이 존재합니다. 데이터 병합을 시작합니다.")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_quizzes = existing_data.get("quiz", [])
        except (json.JSONDecodeError, FileNotFoundError):
            print("기존 파일을 읽는 중 오류가 발생했습니다. 새 파일로 덮어씁니다.")
            existing_quizzes = []

        # 2. 질문을 key로 하는 딕셔너리를 만들어 검색 성능 향상
        quiz_map = {quiz['question']: quiz for quiz in existing_quizzes}
        
        added_count = 0
        updated_count = 0

        # 3. 새로운 퀴즈 데이터를 순회하며 기존 데이터와 비교 및 병합
        for new_quiz in new_quiz_data:
            question = new_quiz['question']
            new_answers = new_quiz['answers']

            # Case 1: 이미 존재하는 문제일 경우
            if question in quiz_map:
                existing_answers_set = set(quiz_map[question]['answers'])
                original_answer_count = len(existing_answers_set)
                
                # 새로운 정답들을 기존 정답 set에 추가 (중복 자동 제거)
                existing_answers_set.update(new_answers)

                # 정답 개수에 변화가 있다면 (새로운 정답이 추가되었다면)
                if len(existing_answers_set) > original_answer_count:
                    # 정렬된 리스트 형태로 다시 저장
                    quiz_map[question]['answers'] = sorted(list(existing_answers_set))
                    updated_count += 1
            
            # Case 2: 새로운 문제일 경우
            else:
                quiz_map[question] = new_quiz
                added_count += 1
        
        # 병합된 퀴즈 딕셔너리의 값들을 리스트로 변환
        final_quiz_list = list(quiz_map.values())
        print(f"병합 완료: {added_count}개 문제 추가, {updated_count}개 문제 업데이트.")

    # 2. 파일이 존재하지 않는 경우, 새로 생성
    else:
        print(f"새로운 파일 '{file_path}'을(를) 생성합니다.")
        final_quiz_list = new_quiz_data
        print(f"저장 완료: {len(new_quiz_data)}개 문제 추가.")

    # 최종 데이터를 JSON 구조에 맞게 정리
    final_data = {"quiz": final_quiz_list}

    # 4. 최종 결과를 파일에 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"퀴즈 데이터가 '{file_path}' 경로에 성공적으로 저장되었습니다.")


# --- 메인 실행 부분 ---
file_name = input("저장할 파일 이름을 입력하세요 (확장자 제외): ")
if file_name:
    quizzes_from_txt = make_quiz_dic()
    if quizzes_from_txt:
        save_or_update_quiz(file_name, quizzes_from_txt)
else:
    print("파일 이름이 입력되지 않았습니다.")