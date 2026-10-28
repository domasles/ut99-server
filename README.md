# Unreal Tournament 1999 Docker server image

Hosting a dedicated server was never this easy. This image also includes mod support! (Through [**RedeeMOD**](https://github.com/domasles/redeemod))

> **NOTE**: This is not anyhow officially affiliated with Epic Games and the Unreal franchise. This project's source does not include any game code or assets and only serves the purpose of attempting to bring UT99 server to Docker infrastructure and add modding support.

## What this aims to be

This Docker package was created out of the need to have a maintained and patched UT99 dedicated server on disposable infrastructure.

While other projects like this already exist, they are often undermaintained and don't include easy modding support.

This project comes with a copy of [**RedeeMOD CLI**](https://github.com/domasles/redeemod/releases/latest) which makes mod management effortless, automatic, and configuring the server straightforward.

RedeeMOD also exists as a GUI app for clients. Check it out [here](https://github.com/domasles/redeemod)!

## How to run the server

Make sure you have **Docker** installed!

Pre-built images exist at [**GitHub Container Registry**](https://ghcr.io/domasles/ut99-server/ut99-server), so to run the server all you have to do is:
```bash
docker compose up
```

Though you might want to tweak a few settings first.

## How to configure the server

After running the container for the first time, `mods/` and `config/` directories should get created wherever the `docker-compose.yml` file is.

Server setup can be controlled using 2 methods.

### Method 1:

| Environment variable | Description | Required? |
|:---|:---|:---:|
| **UT_SERVER_URL** | Startup level, gamemode and more | ✅ |
| **UT_SERVER_NAME** | Name of the server | ✅ |
| **UT_MOTD** | Message of the day (can be up to 4 lines, separated with `\n`) | ❌ |
| **UT_ADMIN_NAME** | Administrator name (cosmetic) | ❌ |
| **UT_ADMIN_EMAIL** | Administrator email (cosmetic) | ❌ |
| **UT_ADMIN_PASSWORD** | Administrator password (used to log in as an admin) | ❌ |
| **UT_GAME_PASSWORD** | Game password (used to connect to a game) | ❌ |
| **UT_WEB_USER** | Web admin panel username | ❌ |
| **UT_WEB_PASSWORD** | Web admin panel password | ❌ |
| **UT_MAX_PLAYERS** | Maximum amount of players | ❌ |
| **UT_UPLINK** | Allows the server to be exposed on public mirrors/lists | ❌ |
| **UT_LAN_ENABLED** | Allows the server to be exposed on LAN | ❌ |
| **UT_WEB_ENABLED** | Enables/disables web admin panel | ❌ |
| **UT_SERVER_PACKAGES** | If a mod has any *.u files, their names without extension must be specified here | ❌ |
| **UT_MODS** | Mod folder names within `mods/` directory | ❌ |

As you can see, only 2 fields are required for the container to run. Any other variable can be left empty, and makes the value internally emptied too.

### Method 2:

Placing a custom-configured `UnrealTournament.ini.template` within `config/` sets it as server's default settings config. Takes a lot of time and **isn't recommended**, unless some very non-standard values are required to be set.

## Building the container

You can build the container yourself by running:
```bash
docker compose up --build -d
```

This will also start the container for you automatically.

## Bottom line

If you need a fast and reliable method to spin up an Unreal Tournament '99 server without worrying about the current state of your installation or setting up a remote installation, this project is for you!

By mixing and applying various mods, you can make custom servers for your friends or communities with ease. Get wild and creative!
