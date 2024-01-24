from graphqlclient import GraphQLClient
import requests
import mimetypes
import os
import sys
import base64
import json
from mwxml import Dump, Page, Upload, Revision
import pandoc
from bs4 import BeautifulSoup

dumpfile = os.getenv("DUMPFILE", "mediawiki_dump.xml")

try:
    input_file = Dump.from_file(open(dumpfile))
except:
    print("Failed opening the dumpfile")
    sys.exit(1)

wikijsurl = os.getenv("GRAPHQLURL", "")
wikijstoken = 'Bearer ' + os.getenv("GRAPHQLKEY", "")

douploads = os.getenv("UPLOAD", str("True")).lower() in ("yes", "y", "true", "1", "t")
docreates = os.getenv("CREATE", str("True")).lower() in ("yes", "y", "true", "1", "t")

client = GraphQLClient(wikijsurl + "/graphql")
client.inject_token(wikijstoken)

def pretty_print_POST(req):
    """
    Some debug function to help sort the failed uploads
    """
    print("{}\n{}\r\n{}\r\n\r\n{}".format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        "\r\n".join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body[:400] 
    ))
    print("--------------END----------------")

def uploadpage(page, revision):
    html = None

    # Quick and dirty
    query = """mutation Page ($content: String!, $description: String!, $editor:String!, $isPublished:Boolean!, $isPrivate:Boolean!, $locale:String!, $path:String!,$tags:[String]!, $title:String!) {
              pages {
                create (content:$content, description:$description, editor: $editor, isPublished: $isPublished, isPrivate: $isPrivate, locale: $locale, path:$path, tags: $tags, title:$title) {
                  responseResult {
                    succeeded,
                    errorCode,
                    slug,
                    message
                  },
                  page {
                    id,
                    path,
                    title
                  }
                }
              }
            }"""

    if revision.text:
        try:
            pan = pandoc.read(obj.text, format="mediawiki")
            html = pandoc.write(pan, format="html")
        except Exception as e:
            print("failed page: {}".format(repr(e)))
            return(False)

        if html:

            # Need to ensure all filenames are lower case
            soup = BeautifulSoup(html, 'html.parser')
            
            img_tags = soup.find_all('img')

            # Iterate through each img tag and update the src attribute to lowercase
            for img_tag in img_tags:
                if 'src' in img_tag.attrs:
                    img_tag['src'] = img_tag['src'].lower()

            html = str(soup)

            # Get rid of special chars
            path = page.title.translate({ord(c): "_" for c in " !@#$%^&*()[]{};:,./<>?\|`~-=_+"})

            queryparams = {
                  "content": html,
                  "description": "article",
                  "editor": "ckeditor",
                  "isPublished": True, 
                  "isPrivate": False, 
                  "locale": "sv", 
                  "path": "/" + path,
                  "tags": [], 
                  "title": page.title
                }


            resp = client.execute(query, queryparams)
            return(resp)

    else:
        return(False)

def uploadfile(Upload):
    headers = {
        'Authorization': wikijstoken
    }

    file = {}

    file["filename"] = Upload.filename
    filecontent = base64.b64decode(Upload.content)
    file["mimetype"], _ = mimetypes.guess_type(Upload.filename)

    files = ( 
              ('mediaUpload', (None, '{"folderId":0}')),
              ('mediaUpload', ('{}'.format(file["filename"]), filecontent, "{}".format(file["mimetype"])))
            )

    rq = requests.Request('POST', wikijsurl + "/u", headers=headers, files=files)
    # pretty_print_POST(rq.prepare())
    result = requests.post(wikijsurl + "/u", headers=headers, files=files) # Actually making the request

    return(result)

if __name__ == "__main__":
    for page in input_file.pages:
        for obj in page:
            if isinstance(obj, Upload) and douploads:
                print("Uploading file {}".format(obj.filename))
                resp = uploadfile(obj)
                if resp and resp.status_code == 200:
                    print("Succeeded")
                    print(resp)
                else:
                    print("Succeeded")
                    print(resp)

            elif isinstance(obj, Revision) and docreates:
                print("Creating page '{}'".format(page.title))
                resp = uploadpage(page, obj)
                try:
                    resp = json.loads(resp)
                except:
                    print("Failed, error translating mediawiki code to html")
                    resp = False
                    continue
                if resp and resp["data"]["pages"]["create"]["responseResult"]["succeeded"]:
                    print("Succeeded, {}".format(resp["data"]["pages"]["create"]["responseResult"]["message"]))
                else:
                    print("Failed, {}".format(resp["data"]["pages"]["create"]["responseResult"]["message"]))

            else:
                print("Object unknown")

