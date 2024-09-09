import local_google
import local_azure
import asyncio
import tomllib


def load_settings():
    with open("data/settings.toml", "rb") as f:
        data = tomllib.load(f)
    return data


async def main():
    settings = load_settings()

    # get birthdays from google contacts
    birthdays = local_google.get_birthdays(settings=settings["google"])

    # update azure calendar
    await local_azure.update_calendar(settings=settings["azure"], birthdays=birthdays)


if __name__ == "__main__":
    asyncio.run(main())
