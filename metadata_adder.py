from pathlib import Path
from mutagen.mp4 import MP4
import requests
from lxml import html
import codecs
import argparse

def get_metadata(_id):
    metadata = {}
    page = requests.get(f"https://www.kink.com/shoot/{_id}")
    tree = html.fromstring(page.content)

    xpath_title = "/html/body/div[2]/div[2]/div[1]/div[4]/div/h1"
    title = tree.xpath(xpath_title)[0].text.strip("\n")
    metadata['title'] = title
    names = []
    description = ""
    for i in range(10):
        try:
            names_xpath = f"/html/body/div[2]/div[2]/div[1]/div[4]/div/div[3]/div[2]/div[1]/p/span[2]/a[{i}]"
            name = tree.xpath(names_xpath)
            names.append(name[0].text.replace(",", ""))
        except IndexError:
            pass
    metadata['names'] = names
    for i in range(10):
        try:
            description_xpath = f"/html/body/div[2]/div[2]/div[1]/div[4]/div/div[3]/div[4]/span/p[{i}]"
            description += tree.xpath(description_xpath)[0].text
            description += "\n"
        except IndexError:
            pass
    metadata['description'] = description
    tags = []
    for i in range(15):
        try:
            tag_path = f"/html/body/div[2]/div[2]/div[1]/div[4]/div/div[3]/div[5]/p[3]/a[{i}]"
            tags.append(tree.xpath(tag_path)[0].text.replace(",", ""))
        except IndexError:
            pass
    
    metadata['tags'] = tags
    return metadata

def update_metadata(files, metafiles, reprocess=False):
    num_files = len(files)
    for index, _file in enumerate(files):
        if _file.replace(".mp4", ".md") in metafiles and not reprocess:
            print(f"progress: {index + 1}/{num_files} processed ({((index + 1) / num_files) * 100} %)")
            continue
        _id = _file.split("\\")[-1].split("_")[0]
        metadata = get_metadata(_id)
        mp4file = MP4(_file)
        tags = ', '.join(metadata['tags'])
        mp4file['©nam'] = metadata['title']
        mp4file['©ART'] = ';'.join(metadata['names'])
        print( mp4file['©ART'])
        mp4file['©cmt'] = tags
        mp4file.pprint()
        readme = []
        with codecs.open(_file.replace(".mp4", ".md"), 'w', encoding='utf-8') as readmefile:
            readme.append("# Metadata\n")
            readme.append("## title\n")
            readme.append(metadata['title'])
            readme.append("## description\n")
            readme.append(metadata['description'])
            readme.append("## tags\n")
            readme.append(f"`{tags}`")
            readme.append("## actors\n")
            readme.append(', '.join(metadata['names']))
            readmefile.writelines('\n'.join(readme))
            
        mp4file.save()
        print(f"progress: {index + 1}/{num_files} processed ({((index + 1) / num_files) * 100} %)")

def get_files(path):
    files = [str(_file) for _file in Path(path).rglob('*.mp4')]
    metafiles = [str(_file) for _file in Path(path).rglob('*.md')]
    return files, metafiles

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to the folder")
    parser.add_argument(
        "--reprocess",
        required=False,
        action='store_true'
     )
    args = parser.parse_args()
    files, metafiles = get_files(args.path)
    reprocess = False
    if args.reprocess:
        reprocess = True
    update_metadata(files, metafiles, reprocess)
