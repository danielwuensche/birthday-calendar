import datetime
from local_classes import Birthday
from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.event import Event
from msgraph.generated.models.patterned_recurrence import PatternedRecurrence
from msgraph.generated.models.recurrence_pattern import RecurrencePattern
from msgraph.generated.models.recurrence_pattern_type import RecurrencePatternType
from msgraph.generated.models.recurrence_range import RecurrenceRange
from msgraph.generated.models.recurrence_range_type import RecurrenceRangeType
from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration


def create_graph_client(client_id, tenant_id, redirect_uri):
    credential = InteractiveBrowserCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        redirect_uri=redirect_uri)
    return GraphServiceClient(credentials=credential) # type: ignore


async def create_event(client: GraphServiceClient, calendar_id: str, subject: str, date: datetime.date, event_reminder_minutes_before_start: int = 15):
    date_start = date
    date_end = date_start + datetime.timedelta(days=1)

    request_body = Event(
        subject=subject,
        is_all_day=True,
        start=DateTimeTimeZone(
            date_time=f"{date_start.isoformat()}T00:00:00",
            time_zone="Europe/Berlin",
        ),
        end=DateTimeTimeZone(
            date_time=f"{date_end.isoformat()}T00:00:00",
            time_zone="Europe/Berlin",
        ),
        recurrence=PatternedRecurrence(
            pattern=RecurrencePattern(
                type=RecurrencePatternType.AbsoluteYearly,
                interval=1,
                month=date_start.month,
                day_of_month=date_start.day
            ),
            range=RecurrenceRange(
                type=RecurrenceRangeType.NoEnd,
                start_date=date_start
            ),
        ),
        reminder_minutes_before_start=event_reminder_minutes_before_start
    )
    await client.me.calendars.by_calendar_id(calendar_id).events.post(body=request_body)

async def update_calendar(settings, birthdays: list[Birthday]):
    # azure connection
    graph_client = create_graph_client(client_id=settings["client_id"], tenant_id=settings["tenant_id"], redirect_uri=settings["redirect_uri"])
    calendars = await graph_client.me.calendars.get()
    calendar_id = None
    for calendar in calendars.value:
        if calendar.name == settings["calendar_name"]:
            calendar_id = calendar.id
            break
    if not calendar_id: # ignore
        print(f"Calendar {settings["calendar_name"]} doesn't exist.")
        exit()

    # get all calendar events
    query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
        top=1000, # per default only 10 results are returned
    )
    request_configuration = RequestConfiguration(
        query_parameters=query_params,
    )
    events = await graph_client.me.calendars.by_calendar_id(calendar_id).events.get(request_configuration=request_configuration)
    events = events.value

    # create calendar events for given birthdays
    for birthday in birthdays:
        event_exists = False
        for event in events:
            if event.subject == f"Birthday {birthday.name}":
                # event for this birthday already exists
                event_exists = True
                break

        if not event_exists:
            await create_event(graph_client, calendar_id, f"Birthday {birthday.name}", birthday.date, event_reminder_minutes_before_start=settings["event_reminder_minutes_before_start"])
            print(f"created Birthday {birthday.name}")