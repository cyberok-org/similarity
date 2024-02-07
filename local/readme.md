# Запуск

- пререквизиты: `python`, `docker`, `docker-compose`
- Исправить `volume path` в `docker-compose`, чтобы они указывали на текущую директорию `db`
- выбрать `ANALYZE` в [consts](consts.py) (название анализируемого json, по ним предподсчитаны данные)
- выбрать подходящий score для алгоритмов (данные посчитаны по дефолтному (хуже него ставить бессмысленно)) - об этом в следующем разделе
- запустить
```bash
python nodes.py
python edges.py
docker-compose up
```

Далее надо импортировать полученные csv.
для этого надо достать id контейнера (`docker ps`) и в нём выполнить
```bash
docker exec -it <container id> bin/neo4j stop
docker exec -it <container id> bin/neo4j-admin database import full --nodes=import/nodes.csv --relationships=import/ssdeep.csv --relationships=import/tlsh.csv --relationships=import/mrsh.csv --relationships=import/nilsimsa.csv --relationships=import/simhash.csv neo4j --overwrite-destination
docker exec -it <container id> bin/neo4j start
```
(если данных нет можно попробовать остановить прошлый `docker-compose up` и после этого запустить его ещё раз - обычно это надо, чтобы локально загрузилось)

После этого можно зайти на http://localhost:7474/browser/ (должен начать работать после compose; login=neo4j, password=aX6Ahj1chae6oe4aiShee5aila4oSho7jeexoo0Ahguo3ZeDiw) и выполнять запросы (пример - [commands](commands.txt))

После окончания надо выполнить (или просто остановить)
```bash
docker-compose down
```

# Дополнительно

## Устаревшее 
(получение метрик работает, но медленно, если оно нужно стоит переписать не на python)

так же можно вывести кластеры в текстовом виде [clusters](rooster/clusters) (текущие результаты про `outputzgrab2443-tls-networks-ru-v3-check-gateway` - список node index), для этого можно запустить [metrics](metrics.py) установив нужные `cluster_score_filter`. Он так же выводит одну метрику по `status_code`, `server`, `vendors` - сколько нод в кластере не имели мажорирующего значения этого параметра - результат от 0 до 1 в среднем по всем кластерам.

По этим метрикам можно построить графики - [metrics_many](metrics_many.py). Они находятся в [pict](rooster/pict) (они строились без ограничений для [edges](edges.py), т.е. с дефолтными аргументами классов). Из того что получилось, к сожалению, ничего нельзя сказать.

## Новое

Eсли нужно получить только кластеры можно использовать [cluster](go/cluster/cluster)

```bash
./go/cluster/cluster -filenameFrom db/import/mrsh.csv -filenameTo rooster/clusters/mrsh.txt -skipScore 30
```

# Детали

- всё запускалось только на `body`
- `tlsh` и `mrsh` для небольших файлов ничего не делают, остальные работают, но не всегда хорошо
- у ноды в http://localhost:7474/browser/ есть `body_path` - можно скопировать и открыть html в браузере
- `nodes2.py` - то же самое, что и `nodes.py`, пригодилось отдельно для 51 порта
- стоит использовать `nodes_big` в `nodes` если данных много - он дольше, но не падает, если данные не влезают в память
