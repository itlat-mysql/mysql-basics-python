# Простейшая программа, показывающая совместную работу Python и MySQL
Программа предназначена только для образовательных целей, использование в коммерческих приложениях не рекомендуется. 

### Системные требования
* **MySQL**, скачивается здесь: [https://www.mysql.com/downloads/](https://www.mysql.com/downloads/)
* **Python**, скачивается здесь: [https://www.python.org/downloads/](https://www.python.org/downloads/)
* **Git**, скачивается здесь: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### Установка


- Склонируйте программу в нужную вам директорию:
```
git clone https://github.com/itlat-mysql/mysql-basics-python.git .
```
- Запустите MySQL сервер и создайте базу данных **example** cо всеми необходимыми данными - файл для создания базы данных (**db-example.sql**) находится в корневой директории данного приложения. 


- В корневой директории приложения создайте файл **.env** и заполните его параметрами для соединения с базой данных. В качестве примера следует использовать файл **example.env**:
```
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=secret
DB_DATABASE=example
DB_CHARSET=utf8mb4
```
- Зайдите в коммандной строке в корневую директорию данного приложения и выполните данные комманды:
```
python -m venv venv
.\venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```
- Затем откройте свой браузер и перейдите по следующему адресу: 
```
http://localhost:8001