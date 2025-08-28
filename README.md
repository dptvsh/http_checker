# HTTP Server Availability Checker

Консольная утилита для тестирования доступности серверов по HTTP/HTTPS протоколу с замером времени ответа и сбором статистики.

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/dptvsh/http_checker.git
cd http_checker

# Установка зависимостей
pip install -r requirements.txt
```

## Использование

### Синтаксис

```bash
python bench.py (-H HOSTS | -F FILE) [-C COUNT] [-O OUTPUT]
```

### Параметры

- `-H, --hosts` - список хостов через запятую (без пробелов)
- `-F, --file` - путь к файлу со списком хостов (по одному на строку)
- `-C, --count` - количество запросов на каждый хост (по умолчанию: 1)
- `-O, --output` - путь к файлу для сохранения результатов

### Примеры запуска

**Тестирование отдельных хостов:**
```bash
python bench.py -H https://ya.ru,https://google.com -C 5
```

**Тестирование хостов из файла:**
```bash
python bench.py -F hosts.txt -C 3 -O results.txt
```

**Одиночный запрос с сохранением результатов:**
```bash
python bench.py -H https://example.com -O output.txt
```

## Пример вывода

```
Host: https://ya.ru
  Success: 3
  Failed: 0
  Errors: 0
  Min time: 0.282s
  Max time: 0.562s
  Avg time: 0.376s

Host: https://google.com
  Success: 3
  Failed: 0
  Errors: 0
  Min time: 0.702s
  Max time: 0.731s
  Avg time: 0.717s

Skipped 1 invalid hosts:
  invalid-url
```

## Формат файла с хостами

Файл должен содержать один URL на строку. Пример (`hosts.txt`):
```
https://ya.ru
https://google.com
https://github.com
https://stackoverflow.com
```

## Обработка ошибок

Программа корректно обрабатывает:
- Невалидные URL (пропускает с предупреждением)
- Ошибки сети и таймауты
- Ошибочные статус-коды (400+)
- Некорректные параметры командной строки

## Примечания

- Для успешных запросов учитываются только ответы со статусом до 400
- Между запросами к одному хосту делается пауза в 1 секунду
- Таймаут запроса установлен в 10 секунд
- В проекте есть готовый файл для тестирования запросов
