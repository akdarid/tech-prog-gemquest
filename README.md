# Технологии программирования

Тетевин Матвей Вадимович, БИВТ-25-4-4.

Лабораторные на Python: ювелирный каталог и текстовая игра «Камни и драконы».

| Лаба | Тема |
| --- | --- |
| 1 | Git, коммиты и ветки |
| 2 | ООП: питомцы, камни, изделия и заказ клиента |
| 3 | Порождающие паттерны в RPG |
| 4 | Структурные и поведенческие паттерны |
| 5 | Тестирование |

Нужен Python 3.9+. Команды из корня проекта:

```bash
python3 -m labs.lab2.main
python3 -m labs.lab3.demo
python3 -m labs.lab4.demo
python3 -m labs.lab4.main
python3 -m unittest discover -s tests -v
```

В игре: `new Матвей warrior`, затем `go forest balanced 2026`. Команда `save` сохраняет героя, `0` завершает игру. Сохранения находятся в `data/heroes.json`.

В `main` собраны все работы. Отдельные этапы: `hotfix/task1`, `lab2-oop`, `lab3-creational`, `lab4-patterns`, `lab5-tests`.
