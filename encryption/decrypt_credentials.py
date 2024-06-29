def decrypt(path_encrypted_credentials="./encryption/"):
    """
     Функция для расшифровки по ключу из окружения
    """
    import os
    from cryptography.fernet import Fernet
    from dotenv import load_dotenv

    # Загрузка переменных окружения из .env
    load_dotenv()
    key = os.getenv('ENCRYPTION_KEY').encode()

    cipher_suite = Fernet(key)

    # Загрузка зашифрованных данных из encrypted_credentials.json
    with open(os.path.join(path_encrypted_credentials, 'encrypted_credentials.json'), 'rb') as f:
        cipher_text = f.read()

    # Дешифрование данных
    credentials = cipher_suite.decrypt(cipher_text).decode()

    # Сохранение расшифрованных данных в origin_credentials.json
    credentials_path = os.path.join(path_encrypted_credentials, 'credentials.json')
    with open(credentials_path, 'w') as f:
        f.write(credentials)

    print(f"Credentials have been decrypted and saved to {credentials_path}.")
    return True