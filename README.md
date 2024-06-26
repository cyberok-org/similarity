# CyberOK - similarity

# Проблема

С ростом количества обрабатываемых сервисов и продуктов становится сложно:
- приоритезировать рассмотрение продуктов
- находить недочеты в уже написанных правилах детектирования продуктов

# Цель

Использовать автоматизированную обработку и нахождение "похожих" сервисов для выделения групп программного обеспечения. Помимо кластеризации в виде текстовых данных используется графическое представление сервисов с их взаимосвязями.

# Структура

- `processing` - начальные преобразование данных, запуск алгоритмов и описание пайплайна обработки. Необходимо для `local` (если нужные данные не даны)
- `local` - скрипты для преобразования выходов алгоритмов в нужные csv и развёртывание локально neo4j с этими данными.
- `go/duplicate` - получение дубликатов по дайджестам для simhash и nilsimsa
- `go/cluster` - получение кластеров по рёбрам
- `checks` - гипотезы, их проверки и скрипты для воспроизведения (на данных по одному порту)

# Алгоритм работы

## Развертывание сервиса

Для загрузки данных требуется развернуть neo4j, кроме этого нужны только данные.

Пример развёртывания через `docker-compose` описан в `local`. Можно альтернативно использовать [neo4j в системе](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-neo4j-on-ubuntu-20-04)

## Загрузка новых данных

### Зависимости

для работы алгоритмов стоит установить каждый из них.

`ssdeep` - https://ssdeep-project.github.io/ssdeep/index.html, по `download` перекинет на релизы - можно скачать код и собрать локально

`tlsh` - https://tlsh.org/, по `download` перекинет на релизы - можно скачать код и собрать локально

`mrsh` - https://www.fbreitinger.de/?page_id=218. Скачать `mrsh_v2.0` и собрать локально

`nilsimsa` - нужен `python`. Установить библиотеку - `pip install nilsimsa`

`simhash` - нужен `python`. Установить библиотеку - `pip install simhash`

### Подготовка данных

#### Требования к входным данным

zgrab2->файлы data, полученные из zgrab2->digest?

#### Формат запуска

### Выбор алгоритма

Саму задачу можно решать нечётким хешированием, этот подход себя зарекомендовал и другие методы не обнаружились. Существует множество различных алгоритмов, было выбрано 5 из них.

Общий комментарий по всем - работают корректно (сложно сравнить между собой из-за разных подходов и не формализуемой метрики), везде есть проблемы с небольшими файлами (либо игнорируются, либо результат считается недостаточно хорошо).

Ориентировочное времени работы (по данным 51 порта) - [time](./processing/time.txt). В целом время работы растёт квадратично от количества данных.

По количеству данных, если брать `ssdeep` за ориентир:
- `mrsh` - получает меньше за счёт того, что игнорирует небольшие файлы
- `tlsh` - на том же уровне примерно, но сильно зависит от ситуации, может выдать в несколько раз меньше данных. В том числе из-за игнорирования. 
- `simhash` - больше, примерно в 1.3 раза
- `nilsimsa` - больше, примерно в 1.5-2 раза
(эти оценки условны, зависят от трешхолда)

Опишем каждый из алгоритмов, дополнительно оценивая время работы, указывая особенности и подходящие. В дальнейшем стоит выбрать 1-2 из них, чтобы не считать и не хранить лишнего.

#### ssdeep

<!-- Сильные/слабые стороны каждого из алгоритмов, ограничения, выбор границы -->

Очень популярный инструмент, написан на `c`.

Работает достаточно долго по сравнению с другими (не критично, если данных не очень много), эта проблема должна решиться при использовании ssdeep-optimize.

По сравнению с другими `score` более значимый (медленнее уменьшается в зависимости от похожести - это значит что `score=30` и `score=80` могут значить разное и нет резкой границы после которой нет дубликатов - вместо этого большой промежуток в котором уменьшается похожесть).

Трешхолд - % схожести (0 - 100), можно ставить 70-80, но находятся дупликаты и при меньших значениях. 20 - около минимально значимой,  70 - более-менее оптимальный, чтобы не потерять нужное.

#### tlsh

Очень популярный инструмент, написан на `c++`.

Работает быстро.

Из проблем - игнорирует небольшие файлы. Есть порты на другие языки.

Трешхолд - расстояние (0 - 9999, меньше - лучше), относительно разумные значения при 55, но может зависеть от данных. Совсем мягкая граница - 300, больше неё смысла ставить нет, 55 - разумная граница, чтобы взять необходимое.

#### mrsh

Написано на `c`, работает медленнее `ssdeep` (если смотреть на том же количестве данных, без уменьшения).

Из проблем - игнорирует небольшие файлы. В целом тоже работает.

Трешхолд - % схожести (0 - 100), можно ставить 30 или меньше (но меньше 20, наверно, не стоит), не что-то пропорциональное `ssdeep`.

#### nilsimsa

Eсть реализация на `python`, выглядит не такой сложной (если смотреть на другие), однако тоже хорошо работает.

Часть со сравнением переписана на [go](./go/duplicate/) и из-за этого работает быстро.

Трешхолд - от -127 до 128. 128 - одинаковые. Можно ставить 110. В целом и с 0 находятся похожие, но данных если ставить меньше 110 может получиться много.

#### simhash

Eсть реализация на `python`, выглядит не такой сложной (если смотреть на другие), однако тоже хорошо работает.

Часть со сравнением переписана на [go](./go/duplicate/) и из-за этого работает быстро.

Трешхолд - расстояние (меньше - лучше), можно ставить 4, мягкая граница - 20.

### Генерация данных

#### Edges

В целом порядок действий для получения `csv` с рёбрами такой:

- выгрузить данные из `json` (см. формат входных данных) - [get_data](./processing/helpers/get_data.py) - выгружает отдельно `body` ([get_data2](./processing/helpers/get_data2.py) - по директории с `json` + специфика - использовалось для `51`)

- запустить каждый из алгоритмов на этих данных и получить дубликаты (в целом если данных много лучше сначала получить дайджесты, а потом посчитать).

##### ssdeep

`ssdeep -d ./data/* -t 70 > ssdeep.txt` - дубликаты

`ssdeep -s ./data/* > ssdeep_digests.txt` - дайджесты

`ssdeep -k ssdeep_digests.txt -s -t 70 ssdeep_digests.txt > ssdeep.txt` - дубликаты по дайджестам (с повторениями)

Если в `data` слишком много файлов возникнет ошибка - `/usr/bin/ssdeep: Слишком длинный список аргументов`

В этом случае стоит переместить всё с `data` в несколько папок (`data0`, `data1`, ...) - для этого есть [parts](./processing/helpers/parts.py)

После этого стоит запустить на каждой `ssdeep`, чтобы получить дайджесты, подправить заголовок и сложить в один файл ([parts](./processing/helpers/parts.sh) - пример, делающий часть этого)

Затем можно запустить `ssdeep` по этим дайджестам и после отдельно пофильтровать (убираем переставленные (оставляем один из `x - y`, `y - x`), одинаковые `x - x` - для всего этого можно брать только `x, y: x < y`) результат (можно это делать вместе с получением `csv` - см. `edges.py`)

(если последнее хочется сделать пооптимальнее, можно использовать [parts_res](./processing/helpers/parts_res.sh) - для этого посчитанные дайджесты не надо объединять, а оставить их в виде `ssdeep_digests{i}.txt`. Получатся два файла - `ssdeep.txt` и `ssdeep_dup.txt`, второй стоит пофильтровать и присоединить к первому)

##### tlsh

`tlsh -xref -r ./data -T 55 > tlsh.txt` - дубликаты

`tlsh -r ./data > tlsh_digests.txt` - дайджесты

`tlsh -xref -l tlsh_digests.txt -T 55 > tlsh.txt` - дубликаты по дайджестам

Если в `data` слишком много (или мало системных ресурсов), поиск дубликатов/дайджестов напрямую может упасть с `segfault`

Если такое происходит можно разделить на несколько директорий, получить дайджесты по каждой и склеить результат - можно использовать [tlsh_digests](./processing/helpers/tlsh_digests.py)

После можно запустить `tlsh` для поиска дубликатов по дайджестам (уже не падает, если ресурсов хватает)

##### mrsh

`./mrsh -g ./data -t 30 > mrsh.txt` - дубликаты

`./mrsh -p ./data_mini` - дайджесты

Проблем с получением сразу дубликатов не возникало, можно использовать сразу этот способ

##### nilsimsa

`python nilsimsa_digests.py` - дайджесты

`python nilsimsa_compare.py` - дубликаты (для чего-то простого можно использовать, но в целом медленный)

Если данных много можно разделить полученный файл с дайджестами на несколько - можно использовать [divide](./processing/helpers/divide.py)

После получения нескольких файлов можно запустить быстрое получение дубликатов (`bathes` - количество файлов, `filePrefix` - прификс файлов, например, файлы имеют вид `nilsimsa/data{i}.html`)

`./duplicate -algorithm nilsimsa -workers 32 -filePrefix nilsimsa/data -bathes 217 -result nilsimsa.txt -threshold 110` - дубликаты 

(выводит сразу `csv`, можно подправить вывод в коде если нужен другой формат)

##### simhash

`python simhash_digests.py` - дайджесты

`python simhash_compare.py` - дубликаты (для чего-то простого можно использовать, но в целом медленный)

Если данных много можно разделить полученный файл с дайджестами на несколько - можно использовать [divide](./processing/helpers/divide.py)

После получения нескольких файлов можно запустить быстрое получение дубликатов (`bathes` - количество файлов, `filePrefix` - прификс файлов, например, файлы имеют вид `simhash/data{i}.html`)

`./duplicate -algorithm simhash -workers 32 -filePrefix simhash/data -bathes 217 -result simhash.txt -threshold 4` - дубликаты 

(выводит сразу `csv`, можно подправить вывод в коде если нужен другой формат)

- преобразовать в `csv` и дополнительно пофильтровать по формату (может пригодиться для `ssdeep`) или по трешхолду - [edges](./local/edges.py)

#### Clusters

`./cluster -filenameFrom mrsh.csv -filenameTo mrsh.txt -skipScore 30 --skipScoreMore=true` - получение кластеров по рёбрам (стоит указывать `skipScore` и `skipScoreMore` - подходящие для алгоритма)

#### Nodes

Для того, чтобы получить ноды можно запустить [nodes](./local/nodes.py), иногда надо дописать специфику (нужно выгрузить что-то дополнительное из `json` или получается некорректный `csv` (пример - `regexes` пришлось сделать строкой, а не листом)). [nodes2](./local/nodes2.py) - запускалось для `51`

Можно запустить `nodes_add_labels` после получения всех кластеров - расставит дополнительно label с указанием кластера (может понадобиться для более удобного поиска/отображения)

### Формат данных

название колонок обусловлены специальным форматом для загрузки в neo4j (например в рёбрах необходимо `:START_ID`, типы типы стоит указывать, иначё всё будет считаться строками и запросы будет делать неудобно).

#### Edges

- :START_ID - id Node.
- :END_ID - id другой Node.
- score:int - метрика похожести, выданная алгоритмом
- :TYPE - название алгоритма (например, `ssdeep`)

#### Nodes

Файл с исходными данными читается построчно, если в `response` содержится `body`, то оно выгружается в отдельный файл, на котором прогоняются алгоритмы. Номер строки в исходном файле является идентификатором для этих данных (например в исходном файле есть `i` строка, данные либо не выгрузятся, если нет `body`, либо будут лежать по пути `data/{i}.html` - можно открыть файл в браузере указав путь до него). Этот номер строки так же является идентификатором ноды.

Для данных по 51 порту - `id` представлен немного иначе, а именно `{port}_{i}`, где `i` - так же как и раньше номер строки, а перед этим идёт порт из соответствующего `json`.

Из исходных данных получены некоторые поля дальше, в качестве описания указан путь до них (если таких данных много (например где-то есть список), то выгружаются все)

- index:ID - id, описанный выше
- path - путь, чтобы можно было открыть в браузере исходный файл.
- ip - .ip
- domain - .domain
- protocol - `http_tls`, `http_ssl`, `http`
- status_code:int - .data.{protocol}.result.response.status_code
- server:string[] - .data.{protocol}.result.response.headers.server
- vendors:string[] - .data.{protocol}.result.products.vendorproductname
- cpe:string[] - .data.{protocol}.result.products.cpe
- regexes - .data.{protocol}.result.products.regex
- :LABEL - лейблы для ноды. Указываются идентификаторы кластеров, к которым принадлежит данная нода.

#### Cluster

В файле (название содержит алгоритм и трешхолд для него) множество строк, в каждой из которых список id Node, составляющих один кластер.

Каждый id встречается 1 раз или не встречается вообще (последнее возможно если он ни с чем не связан - кластеры с 1 нодой не указываются)

Идентификатор кластера - (алгоритм, трешхолд, порядковый номер (кластеры отсортированы по размеру)), например `ssdeep_70_5`.

### Загрузка данных в базу

Получить данные при помощи `zgrab2`.

Получить `Edges`, `Clusters`, `Nodes`.

Для загрузки данных требуется перенести полученные `csv` (для рёбер и нод) в `import` (`mount` куда-то для `compose`, `/var/lib/neo4j/import` или подобное для системы) и затем выполнить (заменив пути, относительно `import` если они отличаются)

```bash
/bin/neo4j stop
cd /var/lib/neo4j/import
/bin/neo4j-admin database import full --nodes=nodes.csv --relationships=mrsh.csv --relationships=nilsimsa.csv --relationships=simhash.csv --relationships=ssdeep.csv --relationships=tlsh.csv neo4j --overwrite-destination
/bin/neo4j start
```

### Сценарии использования

Найти данные для обработки, загрузить их в базу, следуя указаниям из предыдущего пункта.

После можно:

- выполнять запросы в базе (примеры простых запросов - [commands](./local/commands.txt)) 

- исследовать какие-то гипотезы (вычислить что-то по кластерам) и на основе этого строить запросы в базу или просто обрабатывать результат. Пример - [checks](./checks/checks.md)

# Оптимизация сервиса

Можно оптимизировать алгоритмы. Для `ssdeep` - ssdeep-optimize *TBR*. Если использовать как сервис, последнее тоже может пригодиться.

# Направления для развития

- выбрать алгоритм (или несколько) для использования.
