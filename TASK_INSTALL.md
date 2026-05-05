# Установка Task runner

[Task](https://taskfile.dev/) — простой кросс-платформенный аналог `make`. Используется для запуска команд проекта (`task up`, `task test` и т.д.). Команды описаны в [Taskfile.yaml](Taskfile.yaml).

## Установка

### Windows (Chocolatey)

```bash
choco install go-task
```

### Windows (Scoop)

```bash
scoop install task
```

### macOS (Homebrew)

```bash
brew install go-task/tap/go-task
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get install -y golang-github-go-task
```

### Универсальный способ (любая ОС)

```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

Подробнее: https://taskfile.dev/installation/

## Проверка

```bash
task --version
```
