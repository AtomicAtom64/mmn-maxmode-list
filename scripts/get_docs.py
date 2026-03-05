import os
import json

import googleapiclient.discovery as discovery
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'
DOCUMENT_ID = os.getenv('DOCUMENT_ID')

def get_credentials():
    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT"]
    )

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    return creds
  
def read_paragraph_element(element):
  """Returns the text in the given ParagraphElement.

  Args:
      element: a ParagraphElement from a Google Doc.
  """
  text_run = element.get('textRun')
  if not text_run:
    return ''
  return text_run.get('content')


def read_structural_elements(elements):
  """Recurses through a list of Structural Elements to read a document's text
  where text may be in nested elements.

  Args:
      elements: a list of Structural Elements.
  """
  text = ''
  for value in elements:
    if 'paragraph' in value:
      elements = value.get('paragraph').get('elements')
      for elem in elements:
        text += read_paragraph_element(elem)
    elif 'table' in value:
      # The text in table cells are in nested Structural Elements and tables may
      # be nested.
      table = value.get('table')
      for row in table.get('tableRows'):
        cells = row.get('tableCells')
        for cell in cells:
          text += read_structural_elements(cell.get('content'))
    elif 'tableOfContents' in value:
      # The text in the TOC is also in a Structural Element.
      toc = value.get('tableOfContents')
      text += read_structural_elements(toc.get('content'))
  return text

def fetch_document():
    """Fetch the Google Doc with tab content included."""
    creds = get_credentials()

    docs_service = discovery.build(
        'docs', 'v1',
        credentials=creds,
        discoveryServiceUrl=DISCOVERY_DOC
    )

    return (
        docs_service.documents()
        .get(documentId=DOCUMENT_ID, includeTabsContent=True)
        .execute()
    )


def extract_tab_text(tab):
    """Extract full text from a tab."""
    document_tab = tab.get('documentTab')
    body = document_tab.get('body', {})
    content = body.get('content', [])
    return read_structural_elements(content)


def get_main_list() -> str:
    """Reads the first tab (index 0)."""
    try:
        doc = fetch_document()
        tabs = doc.get('tabs', [])

        if len(tabs) < 1:
            print("No tabs found.")
            return ""

        return extract_tab_text(tabs[0]) or ""

    except HttpError as error:
        print(f'An error occurred: {error}')
        return ""


def get_sl_list() -> str:
    """Reads the second tab (index 1)."""
    try:
        doc = fetch_document()
        tabs = doc.get('tabs', [])

        if len(tabs) < 2:
            print("Second tab not found.")
            return ""

        return extract_tab_text(tabs[1]) or ""

    except HttpError as error:
        print(f'An error occurred: {error}')
        return ""