# quiz_parser.py

class QuizParser:
    """텍스트를 퀴즈 데이터로 변환하는 클래스"""

    def parse_file_into_blocks(self, full_text: str):
        """
        파일을 ':+ ...' 줄을 경계로 블록 분리합니다.
        마지막 블록은 EOF까지 포함합니다.
        """
        blocks, cur = [], []
        for raw in full_text.splitlines():
            if raw.strip().startswith(":+"):
                blocks.append("\n".join(cur))
                cur = []
            else:
                cur.append(raw)
        blocks.append("\n".join(cur))  # 마지막 블록 push
        return blocks
    
    def parse_quiz_block(self, text_block: str):
        """
        한 문항 블록을 파싱하여 문제, 정답, 힌트를 추출합니다.
        - 일반 줄  → 문제 본문 누적
        - ':!' 줄  → 힌트 (마지막 값으로 갱신)
        - ':=' 줄  → 정답 ('||' 로 다중 정답)
        """
        lines = text_block.splitlines()

        # 선행/후행 빈 줄 제거
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        lines = lines[i:]

        j = len(lines) - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        lines = lines[:j+1]

        q_lines, answers, hint = [], [], None

        for raw in lines:
            line = raw.rstrip("\n")
            s = line.strip()

            if not s:
                q_lines.append("") 
                continue

            if s.startswith(":!"):
                hint = s[2:].strip() or None
            elif s.startswith(":="):
                cand = [a.strip() for a in s[2:].split("||") if a.strip()]
                if cand:
                    answers = cand
            elif s.startswith(":+"):
                continue
            else:
                q_lines.append(line)

        question_text = "\n".join(q_lines).strip()
        return question_text, answers, hint
