# binance-btcusdt-price
Несколько микросервисов на python + influxdb + grafana чтобы показывать btc/usdt курс с Binance.

## Устройство репозитория
Все микросервисы лежат в одной монорепе в папке <b>microservices</b>.

Общий код для микросервисов лежит в папке <b>common</b> и копируется в микросервис на этапе сборки контейнера.

В корне также лежит dev-конфигурация (<b>clusters_dev.toml</b>), dev-template (<b>dev.Dockerfile</b>) для создания контейнера микросервиса и <b>Makefile</b> 
для быстрой сборки.

Команды из терминала для сборки проекта:
- <i>make all</i> - запустить микросервисы + InfluxDB + Grafana
- <i>make stop</i> - очистить запущенный контекст и удалить контейнеры (вызывается в начале all)

Внутри микросервиса лежат:
- код микросервиса
- <b>requirements.txt</b> - зависимости для venv 
- <b>deployment_dev.yaml</b> - кубер-конфиг для поднятия dev-кластера микросервисов данного типа

### Что можно было бы доработать:
- в данный момент можно для отладки поднимать микросервисы локально каждый через venv, но для этого требуется некоторое количество действий в IDE - эти действия можно было бы автоматизировать
- сделать common отдельным пакетом для virtualenv и подтягивать его через venv, а не копированием
- добавить тесты

## Архитектура решения
Три микросервиса:
- <b>crawler</b> - ходит на Binance за данными стаканов и отправляет их в <b>converter</b> и <b>storer</b>
- <b>converter</b> - берет стакан, преобразует его в честную цену и отправляет ее в <b>storer</b>
- <b>storer</b> - получает стакан и честную цену и складывает их в БД

Каждый инстанс микросервиса работает в своем изолированном окружении <b>docker-контейнера</b>. 

Для оркестрации микросервисов поднимается <b>Kubernetes</b> который создает реплики, проксирует между ними запросы, перезапускает их в случае падения.
Dev-конфиг для Kubernetes лежит в корне каждого микросервиса.

Плюсы работы с Kubernetes:
- удобное конфигурирование ресурсов, кластеров и инстансов микросервисов
- при правильном устройстве система становится достаточно fault-tolerant, кубер умеет сам переподнимать упавшие контейнеры, а распределенный на несколько серверов кластер не упадет даже при падении одной из машин
- решение масштабируется, то есть может выдержать большую нагрузку (в идеале любую)

Про нагрузку: бутылочным горлышком системы является crawler - он не позволяет масштабироваться для скачивания одних и тех же данных, с другой стороны - его можно реплицировать для скачивания разных данных.

База данных - <b>InfluxDB</b>.

Выбор в пользу influx был сделан так как эта БД лучше всего подходит для хранения и извлечения временных данных. 
Данные устроены несложно, а вся работа с ними заключается в том что мы в основном строим по ним графики, в таком случае Time-series DB подходят лучше всего, а NoSQL-решения однозначно выигрывают у реляционных.

InfluxDB поднимается в отдельных docker-контейнерах.

Grafana тоже поднимается в отдельном docker-контейнере и ходит за данными в БД.

### Что можно было бы доработать:
- поднять InfluxDB в Kubernetes
- подумать как можно реплицировать crawler для скачивания одних и тех же данных
- втащить Grafana в кубер, это не дало бы большого импакта, но было бы удобнее конфигурировать

### Почему в репе dev-Dockerfile и dev-конфиги для Kubernetes?
Обычно конфигурации кластеров для прода хранятся в отдельной репе для того чтобы разделять инфраструктуру и разработку.
В таком случае на этапе пушей в гит работают CI/CD-пайплайны и туда подкладываются prod-конфиги.

## Как это запустить локально? (macOS)
1. Для того чтобы поднять систему локально нужно скачать Docker Desktop (https://www.docker.com/products/docker-desktop).
2. Нужно запустить Docker Desktop и в Preferences->Kubernetes активировать галочку "Enable Kubernetes".
3. Затем запустить make all.
4. После этого зайти в Grafana (http://localhost:3000), логин/пароль: admin/admin
5. В Grafana зайти в Configuration->Data Sources нажать "Add data source", выбрать InfluxDB
6. В URL ввести: http://localhost:8086, в Access: Browser, в Database: fair_price.
7. Затем можно создавать все нужные графики и дашборды.
 
