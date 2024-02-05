## commands

./mrsh -g ./data -t 30 > mrsh.txt

ssdeep -d ./data/* -t 30 > ssdeep.txt

tlsh -xref -r ./data -T 55 > tlsh.txt

python simhash_digests.py
python simhash_compare.py   (or use go/duplicate)

python nilsimsa_digests.py
python nilsimsa_compare.py  (or use go/duplicate)

## limits

soft:
ssdeep 20; tlsh 300; mrsh 20; nilsimsa 0; simhash 20;

hard:
ssdeep 70; tlsh 55; mrsh 30; nilsimsa 110; simhash 4;

## peculiarities

В целом если данных много лучше сначала получить дайджесты, а потом посчитать.

### ssdeep

`ssdeep -d ./data/* -t 70 > ssdeep.txt` - дубликаты

`ssdeep -s ./data/* > ssdeep_digests.txt` - дайджесты

`ssdeep -k ssdeep_digests.txt -s -t 70 ssdeep_digests.txt > ssdeep.txt` - дубликаты по дайджестам (с повторениями)

Если в `data` слишком много файлов возникнет ошибка - `/usr/bin/ssdeep: Слишком длинный список аргументов`

В этом случае стоит переместить всё с `data` в несколько папок (`data0`, `data1`, ...) - для этого есть [parts](./helpers/parts.py)

После этого стоит запустить на каждой `ssdeep`, чтобы получить дайджесты, подправить заголовок и сложить в один файл ([parts](./helpers/parts.sh) - пример, делающий часть этого)

Затем можно запустить `ssdeep` по этим дайджестам и после отдельно пофильтровать (убираем переставленные (оставляем один из `x - y`, `y - x`), одинаковые `x - x` - для всего этого можно брать только `x, y: x < y`) результат (можно это делать вместе с получением `csv` - см. `edges.py`)

### tlsh

`tlsh -xref -r ./data -T 55 > tlsh.txt` - дубликаты

`tlsh -r ./data > tlsh_digests.txt` - дайджесты

`tlsh -xref -l tlsh_digests.txt -T 55 > tlsh.txt` - дубликаты по дайджестам

Если в `data` слишком много (или мало системных ресурсов), поиск дубликатов/дайджестов напрямую может упасть с `segfault`

Если такое происходит можно разделить на несколько директорий, получить дайджесты по каждой и склеить результат - можно использовать [tlsh_digests](./helpers/tlsh_digests.py)

После можно запустить `tlsh` для поиска дубликатов по дайджестам (уже не падает, если ресурсов хватает)

### mrsh

`./mrsh -g ./data -t 30 > mrsh.txt` - дубликаты

`./mrsh -p ./data_mini` - дайджесты

Проблем с получением сразу дубликатов не возникало, можно использовать сразу этот способ

### nilsimsa

`python nilsimsa_digests.py` - дайджесты

`python nilsimsa_compare.py` - дубликаты (для чего-то простого можно использовать, но в целом медленный)

Если данных много можно разделить полученный файл с дайджестами на несколько - можно использовать [divide](./helpers/divide.py)

После получения нескольких файлов можно запустить быстрое получение дубликатов (`bathes` - количество файлов, `filePrefix` - прификс файлов, например, файлы имеют вид `nilsimsa/data{i}.html`)

`./duplicate -algorithm nilsimsa -workers 32 -filePrefix nilsimsa/data -bathes 217 -result nilsimsa.txt -threshold 110` - дубликаты 

(выводит сразу `csv`, можно подправить вывод в коде если нужен другой формат)

### simhash

`python simhash_digests.py` - дайджесты

`python simhash_compare.py` - дубликаты (для чего-то простого можно использовать, но в целом медленный)

Если данных много можно разделить полученный файл с дайджестами на несколько - можно использовать [divide](./helpers/divide.py)

После получения нескольких файлов можно запустить быстрое получение дубликатов (`bathes` - количество файлов, `filePrefix` - прификс файлов, например, файлы имеют вид `simhash/data{i}.html`)

`./duplicate -algorithm simhash -workers 32 -filePrefix simhash/data -bathes 217 -result simhash.txt -threshold 4` - дубликаты 

(выводит сразу `csv`, можно подправить вывод в коде если нужен другой формат)

## Pipeline

### Edges

В целом порядок действий для получения `csv` с рёбрами такой:

- выгрузить данные из `json` - [get_data](./helpers/get_data.py) - выгружает отдельно `body` ([get_data2](./helpers/get_data2.py) - по директории с `json` + специфика - использовалось для `51`)

- запустить каждый из алгоритмов на этих данных и получить дубликаты (детальнее по каждому описано выше)

- преобразовать в `csv` и дополнительно пофильтровать по формату (может пригодиться для `ssdeep`) или по трешхолду - [edges](./../local/edges.py)

### Clusters

`./cluster -filenameFrom mrsh.csv -filenameTo mrsh.txt -skipScore 30 --skipScoreMore=true` - получение кластеров по рёбрам (стоит указывать `skipScore` и `skipScoreMore` - подходящие для алгоритма)

### Nodes

Для того, чтобы получить ноды можно запустить [nodes](../local/nodes.py), иногда надо дописать специфику (нужно выгрузить что-то дополнительное из `json` или получается некорректный `csv` (пример - `regexes` пришлось сделать строкой, а не листом)). [nodes2](../local/nodes2.py) - запускалось для `51`

Можно запустить `nodes_add_labels` после получения всех кластеров - расставит дополнительно label с указанием кластера (может понадобиться для более удобного поиска/отображения)

### Neo4j

полученные рёбра и ноды можно залить в `neo4j`. Для этого лучше использовать `neo4j-admin`, пример (для `compose` надо немного иначе, инструкция - [local](../local/readme.md)):

- положить `csv` в `/var/lib/neo4j/import`

- поочерёдно выполнить следующее:

```bash
sudo /bin/neo4j stop
cd /var/lib/neo4j/import
sudo /bin/neo4j-admin database import full --nodes=nodes.csv --relationships=mrsh.csv --relationships=nilsimsa.csv --relationships=simhash.csv --relationships=ssdeep.csv --relationships=tlsh.csv neo4j --overwrite-destination
sudo /bin/neo4j start
```

## Other

[tools](./tools.md) - что-то про инструменты (алгоритмы, что здесь и другие)

[helpers](./helpers/) - вспомогательные скрипты, упоминаются выше

[local](../local/readme.md) - дополнительная информация по дальнейшему + про алгоритмы

[time](time.txt) - ориентировочное время работы скриптов (на примере данных по 51 порту)
