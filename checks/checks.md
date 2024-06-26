# main

Связанные файлы находятся в [папке](checks/res) с соответствующим номером (кроме 4 - для неё результат в 3).

1) Добавился [clusters_checks](clusters_checks.py) `by_products` - сохраняет по алгоритму множество `json` (номер равен строке в файле с кластерами на основе которых было построено (в свою очередь они отсортированы по размеру кластера)). Каждый такой `json` содержит `data` - мапа: имя вендора в количество нод в кластере, в котором он есть. `most_popular_vendor` - вендор кластера (самый популярный в нём, если их несколько назначается случайный), `len` - количество нод в кластере. `cluster` - индексы нод кластера (по сути строчка из соответствующего файла с кластерами).
Для случая если вендоров нет (пустой список) - используется значение `<empty>`.
В итоге получилось слишком много нужных кластеров (большая часть подходит под описание), смотреть на кластеры так всё равно удобнее, чем на файл с индексами нод в кластерах - тут есть больше вспомогательной информации по которой можно понять интересен кластер или нет.
Думаю можно добавить ещё условий/пофильтровать кластеры, чтобы на это можно было смотреть удобнее, но пока так.
2) Получены (скрипт - [cokhostdomains_checks](cokhostdomains_checks.py)) кластеры по `outputzgrab2443-tls-cokhostdomains.json` (`clusters`), замена индекса ноды на домен кластера (`cokhostdomains`) - все данные взяты с одного `ip` так что нет разделения по нему. Можно заметить, что часто в кластере домены чем-то похожи.
Было подсчитана длина максимальной общей подстроки среди доменов для каждого кластера (возможно это не очень честная (часто встречается `website`, домен и прочие подстроки) и показательная метрика, так что стоит относиться к ней с осторожностью). По ней были построены диаграммы: количество кластеров по длине общей подстроки. Картинки в `pict`. По этим данным в среднем длина по всем алгоритмам - между `18` и `19`.
3) В ноду добавлены лейблы (`nodes_add_labels` в [nodes](nodes.py)). Их смысл в том, чтобы упростить запросы (вернее сделать так, чтобы было вообще реально запросить) для того, чтобы смотреть как кластер разбивается на подкластеры при уменьшении трешхолда алгоритма. Так же введено представление данных ([clusters_checks](clusters_checks.py) `create_cluster_structure` - создаётся тут), позволяющие доставать интересные лейблы с точки зрения разделения кластера ([clusters_checks](clusters_checks.py) `interesting_cluster_decompositions` - берутся случаи, подходящие под условие (можно определять при запуске - функция), на выходе файл: кластер, который был -> кластеры, на которые распалось (кластеры из `1` ноды не интересны и игнорируются)).
Результат можно превратить в запрос самостоятельно или автоматизировать, если это надо.
4) В ноду добавлено регулярное выражение. По полученной в `3` структуре можно в том числе выбрать подходящую "функцию интересности" (`interesting_cluster_check_different_regexes` или написать что-то похожее) - в результате выберутся подкластеры с разными `regex`, которые на шаге до (с менее точным трешхолдом) были в одном кластере.
5) Считалась следующая метрика для кластера: находился `vendor` (или `server` и `regexes` аналогично), который встречается в кластере чаще всего. Считалось отношение нод в кластере, содержащих его к общему число нод в этом кластере. На других данных эта метрика всегда была `1` даже при не очень большом трешхолде (это значит, что в каждом кластере был `vendor`, который был в каждой его ноде). На всём `443` порту эта метрика всё же стала не `1`.
Отдельно по `server`, `vendor` и `regexes` (далее в описании, для простоты, речь о конкретно вендоре) (в [clusters_checks](clusters_checks.py) `metric`) проверяется эта метрика, и если она не `1` (параметризуется в общем случае), то сохраняется `json`, содержащий `max` - число нод, содержащих самый популярный вендор, `count` - число нод в кластере, `k` - отношение `max` и `count` (= значение метрики), `data` и `cluster` - вендоры и индексы нод кластера соответственно (тот же формат, что и в `1`)
Чтобы это анализировать можно предварительно пофильтровать/посортировать по добавленным значениям `max`, `count` и `k` в зависимости от того, что хочется или смотреть как есть в отсортированном по `count` виде.
По этим данным можно попытаться определять склеенные кластеры (не очень большое значение `k` и относительно небольшое отличие `2` максимума `data` от `max`) и в целом большие кластеры с небольшим `k` могут быть интересны.

По всем пунктам есть скрипты, их можно модифицировать в случае если хочется получить что-то похожее/исправить то, что есть.

## Interesting clusters

По результатам 3, 4 получаются файлы по алгоритмам, каждый из которых содержит подобные строки:
```bash
ssdeep_80_1229: ssdeep_90_1579 ssdeep_90_3007
```

Это означает что `ssdeep` с трешхолдом 80 нашёлся кластер (все его ноды помечены лейблом `ssdeep_80_1229`), при увеличении трешхолда (до 90) он распался на 2 других - c указанными лейблами. Так же эта конструкция должна удовлетворять условию с которым этот файл был получен - например, при запуске с `interesting_cluster_check_different_vendors` - у нод на которые распались будут различные вендоры (самые популярные вендоры в них).

Можно выполнить, например, такие запросы:

Весь большой кластер (так же может быть удобно, например, добавлять цвета по лейблу)
```bash
MATCH (n:ssdeep_80_1229) RETURN n
```

Ноды обоих подкластеров
```bash
MATCH (n) WHERE n:ssdeep_90_1579 OR n:ssdeep_90_3007 RETURN n
```

Связи между подкластерами (для подобных запросов стоит отключать `Connect result nodes` - галочка в настройках из браузера)
```bash
MATCH (n:ssdeep_90_1579)-[alg:ssdeep]->(m:ssdeep_90_3007) RETURN n, m, alg
```

Связи в кластере с определённым трешхолдом алгоритма (для подобных запросов стоит отключать `Connect result nodes` - галочка в настройках из браузера)
```bash
MATCH (n:ssdeep_80_1229)-[alg:ssdeep]->(m:ssdeep_80_1229) WHERE alg.score >= 90 RETURN n, m, alg
```

Число нод в кластере
```bash
MATCH (n:ssdeep_80_1229) RETURN count(n)
```

## Примеры

### много кластеров, разные интересующие вендоры

(можно переключить надпись на ноде на вендора)

```bash
MATCH (n:tlsh_30_391)-[alg:tlsh]->(m:tlsh_30_391) WHERE alg.score <= 15 RETURN n, m, alg
```

```bash
MATCH (n:nilsimsa_110_231)-[alg:nilsimsa]->(m:nilsimsa_110_231) WHERE alg.score >= 120 RETURN n, m, alg
```

## разные regex

```bash
MATCH (n) WHERE n:ssdeep_80_1611 OR n:ssdeep_80_1655 OR n:ssdeep_80_2093 RETURN n
```

```bash
MATCH (n:ssdeep_70_818)-[alg:ssdeep]->(m:ssdeep_70_818) WHERE alg.score >= 80 RETURN n, m, alg
```

<!--
ssdeep - 70 80 90 95
mrsh - 30 50 70 90
nilsimsa - 100 110 120 125
tlsh - 55 30 15 5
simhash - 4 3 2 1
-->
