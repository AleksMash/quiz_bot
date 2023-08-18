import json, random, glob

from pathlib import Path
import argparse

from dotenv import load_dotenv

def make_json_file():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, default='raw_data/',
                        help='Путь к каталогу с текстовыми файлами')
    parser.add_argument('-c', '--filecount', type=int, default=5,
                        help='Число случайно отбираемых для обработки файлов')
    args = parser.parse_args()
    questions = {}
    files = glob.glob(str(Path(args.directory, '*.txt')))
    files_selected = random.sample(files, args.filecount)
    for file in files_selected:
        with open(file, "r", encoding="KOI8-R") as file_io:
            file_contents = file_io.read()
        splitted_file = file_contents.split('\n\n')

        for block in splitted_file:
            block = block.strip('\n')
            if block.startswith('Вопрос'):
                question_splitted = block.split('\n')
                del question_splitted[0]
                question = ' '.join(question_splitted)
            elif block.startswith('Ответ'):
                if not question:
                    print(block)
                    raise Exception('Найден ответ до обнаружения вопроса')
                answer_splitted = block.split('\n')
                del answer_splitted[0]
                answer = ' '.join(answer_splitted)
                questions[question] = answer
                question = None

    with open('quiz.json', 'w', encoding='UTF-8') as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)

    print('Файл quiz.json для работы чат-бота сформирован')
    print(f'В каталоге "{args.directory}" обработано {args.filecount} файлов')

if __name__ == '__main__':
    make_json_file()