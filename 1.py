import psycopg2
from config import params
import csv

def create_table():
    command = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL
    )
    """
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(command)
            conn.commit()
    print("Таблица phonebook создана.")

def insert_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # пропускаем заголовок
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                for row in reader:
                    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
                conn.commit()
    print("Данные загружены из CSV.")

def insert_from_console():
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
            conn.commit()
    print("Данные добавлены.")

def update_data():
    name = input("Введите имя пользователя для обновления: ")
    new_phone = input("Введите новый номер: ")
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
            conn.commit()
    print("Обновление завершено.")

def query_data():
    key = input("Введите имя или часть номера для поиска: ")
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s OR phone LIKE %s", ('%' + key + '%', '%' + key + '%'))
            results = cur.fetchall()
            for row in results:
                print(row)

def delete_data():
    field = input("Удалить по (name/phone): ").strip()
    value = input("Введите значение: ").strip()
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM phonebook WHERE {field} = %s", (value,))
            conn.commit()
    print("Удаление выполнено.")

def main():
    create_table()
    while True:
        print("\nМеню:")
        print("1. Добавить из CSV")
        print("2. Добавить вручную")
        print("3. Обновить номер")
        print("4. Поиск")
        print("5. Удалить")
        print("6. Выйти")
        choice = input("Выберите опцию: ")
        if choice == '1':
            insert_from_csv("contacts.csv")
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_data()
        elif choice == '4':
            query_data()
        elif choice == '5':
            delete_data()
        elif choice == '6':
            break
        else:
            print("Неверный ввод")

if __name__ == '__main__':
    main()