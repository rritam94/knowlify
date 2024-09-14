from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

def create_presentation(title, email_to_share):
    creds = Credentials.from_service_account_file('client_key.json')

    try:
        service = build("slides", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        body = {"title": title}
        presentation = service.presentations().create(body=body).execute()
        presentation_id = presentation.get('presentationId')
        print(f"Created presentation with ID: {presentation_id}")

        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email_to_share
        }
        drive_service.permissions().create(
            fileId=presentation_id,
            body=user_permission,
            fields='id'
        ).execute()
        print(f"Presentation shared with {email_to_share}")

        return presentation_id

    except HttpError as error:
        print(f"An error occurred: {error}")
        print("Presentation not created")
        return error

def create_slide(presentation_id, slide_title, slide_content):
    creds = Credentials.from_service_account_file('client_key.json')

    try:
        service = build("slides", "v1", credentials=creds)

        requests = [
            {
                "createSlide": {
                    "insertionIndex": 0,
                    "slideLayoutReference": {
                        "predefinedLayout": "TITLE_AND_BODY"
                    }
                }
            }
        ]

        body = {"requests": requests}
        
        response = (
            service.presentations()
            .batchUpdate(presentationId=presentation_id, body=body)
            .execute()
        )
        
        create_slide_response = response.get("replies")[0].get("createSlide")
        created_slide_id = create_slide_response.get('objectId')
        
        slide = service.presentations().pages().get(presentationId=presentation_id, pageObjectId=created_slide_id).execute()
        title_placeholder_id = None
        body_placeholder_id = None

        for element in slide.get('pageElements', []):
            if 'shape' in element:
                placeholder = element['shape'].get('placeholder', {})
                if placeholder.get('type') == 'TITLE':
                    title_placeholder_id = element['objectId']
                elif placeholder.get('type') == 'BODY':
                    body_placeholder_id = element['objectId']

        requests = [
            {
                "insertText": {
                    "objectId": title_placeholder_id,
                    "insertionIndex": 0,
                    "text": slide_title
                }
            },
            {
                "insertText": {
                    "objectId": body_placeholder_id,
                    "insertionIndex": 0,
                    "text": slide_content
                }
            }
        ]
        
        body = {"requests": requests}
        
        response = (
            service.presentations()
            .batchUpdate(presentationId=presentation_id, body=body)
            .execute()
        )
        
        print(f"Created slide with ID: {created_slide_id}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        print("Slide not created")
        return error

    return response

def create_completed_slideshow(json):
    # id = create_presentation('Test Presentation', 'rritam94@gmail.com')

    # for item in reversed(json):
    #     title = item['title']
    #     bullet_points = item['bullet_points']
    #     slide_content = '\n'.join(bullet_points)
    #     create_slide(id, title, slide_content)

    # return id

    slides = []
    for item in (json):
        title = item['title']
        bullet_points = item['bullet_points']
        slides.append({
            "title": title,
            "points": bullet_points
        })

    return slides