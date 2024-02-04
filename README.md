# similarity

Содержание:

- [processing](./processing/readme.md) - начальные преобразование данных, запуск алгоритмов и описание пайплайна обработки. Необходимо для [local](./local/readme.md) (если нужные данные не даны)
- [local](./local/readme.md) - скрипты для преобразования выходов алгоритмов в нужные `csv` и развёртывание локально `neo4j` с этими данными.
- [go/duplicate](./go/duplicate/) - получение дубликатов по дайджестам для `simhash` и `nilsimsa`
- [go/cluster](./go/cluster/) - получение кластеров по рёбрам
- [checks](./checks/checks.md) - гипотезы, их проверки и скрипты для воспроизведения (на данных по одному порту), подробнее о задачах - [тут](https://cyberok.gitlab.yandexcloud.net/cok/rooster/analytics/-/issues/253)
