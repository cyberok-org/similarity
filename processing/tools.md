- SpotSigs
- Shingling
- I-Match
- DURIAN
- ANDD

## Инструменты
- [ssdeep](https://ssdeep-project.github.io/ssdeep/index.html)
- [sdhash](https://github.com/sdhash/sdhash)
- [TLSH](https://tlsh.org/)
- [mrsh](https://www.fbreitinger.de/?page_id=218)
- [nilsimsa](https://pypi.org/project/nilsimsa/)
- [SpotSigs](https://github.com/luismmontielg/spotsigs)
- [simhash](https://pypi.org/project/simhash/)
- minhash

## Другое
- предобработка
- специальная модель для небольших кусков (suf tree?)

## refs
- https://en.wikipedia.org/wiki/Content_similarity_detection
- https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/
- https://arxiv.org/pdf/2109.08789.pdf

- https://storage.googleapis.com/pub-tools-public-publication-data/pdf/33026.pdf
- https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=113ee8cefb82945e2d9e8ade44c23d995599b60f
- https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=ea40c4d6198ee721258e16dc6e0ccad1853aed66
- https://www.diggov.org/library/library/dgo2006/dgo2006.pdf#page=265


https://arxiv.org/pdf/2210.04261.pdf
https://aclanthology.org/2020.lrec-1.156.pdf


### Check <!-- [0, 50) -->
- 11 - ssdeep нашёл не всё
- 20, 28 - nilsimsa считает похожими разные небольшие входы
- 22 - разное ранжирование
- 25 - tlsh, mrsh - быстро уменьшаются метрики
- 26 - неоднозначные разные оценки
- 29 - разное ранжирование
- 34 - tlsh не нашёл 4503
- 45 - tlsg - большая метрика
- 49 - все кроме nilsimsa, большая метрика/не находят

### Other

[tools](./tools.md) - что-то про инструменты (алгоритмы, что здесь и другие)

[helpers](./helpers/) - вспомогательные скрипты, упоминаются выше

[local](../local/readme.md) - дополнительная информация по дальнейшему + про алгоритмы

[time](time.txt) - ориентировочное время работы скриптов (на примере данных по 51 порту)
