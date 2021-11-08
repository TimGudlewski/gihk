import wget, os, helpers

images_dir = os.path.join(helpers.gihk_dir, 'images')


def main():
    collection = helpers.read_json_file(os.path.join(helpers.gihk_dir, 'collection.json'))
    for record in collection:
        output_dirname = record['title'].replace(' ', '_')
        output_dir = os.path.join(images_dir, output_dirname)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for img_type in ['main', 'scene']:
            print(record[img_type])
            filename = wget.download(record[img_type], out=f'images\\{output_dirname}\\')
            os.rename(filename, os.path.join(output_dir, f'{img_type}.jpg'))


if __name__ == '__main__':
    main()
