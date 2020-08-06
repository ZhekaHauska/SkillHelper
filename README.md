# Skill Helper
Интерактивные заметки для долгосрочного планирования.

Приложение призвано помочь в развитии желаемых навыков, организации рабочего пространства и борьбе с прокрастинацией.

# Установка
## Установка готовой сборки
В [релизах](https://github.com/ZhekaHauska/SkillHelper/releases) можно найти свежие версии програмы для Windows и GNU/Linux. Для установки достаточно распаковать архив `SkillHelper-x.xx-your_os.tar.gz`. В папке `SkillHelper-x.xx-your_os` находится
файл `SkillHelper`, который нужно сделать исполняемым и использовать для запуска программы.

**Замечание для пользователей GNU/Linux:** Для работы программы требуется `libс` версии не ниже **2.31**. Чтобы проверить версию `libc` введите в терминале `ldd --version`.

**Замечение для пользователей Windows:** На данный момент поддерживается только Windows 10.

## Ручная сборка
Ручную сборку рекоменуется проводить с помощью `pyinstaller`. Для этого сначала нужно создать окужение с необходимыми пакетами, полный список которых можно найти в файле [`environment.yml`](https://github.com/ZhekaHauska/SkillHelper/blob/connections/environment.yml) данного репозитория, например, с помощью [Anaconda](https://www.anaconda.com): `conda env create -f environment.yml`, будет создано окружение под названием `skill_helper`. Не забудьте его активировать перед продолжением: `conda activate skill_helper`. Перед сборкой желательно проверить работоспособность программы запустив [`main.py`](https://github.com/ZhekaHauska/SkillHelper/blob/connections/main.py) командой: `python main.py`. При необходимости `pyinstaller` можно установить командой `pip install pyinstaller`. Осуществить сборку, находясь в директории с `main.py`, можно командой `pyinstaller main.spec`. Готовая сборка будет находится в папке `dist`.    

**Требования:** Для работы программы требуется `Python` версии не ниже **3.82**, `kivy` версии не ниже **1.11.1**, `pandas` версии не ниже **1.0.5**, 
`pyaml` версии не ниже **0.2.5**. 
