#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import boto3
import zipfile
import sys


def zip_project(project_path):
    if not project_path:
        project_path = os.getcwd()

    project_name = os.path.basename(project_path)
    project_zip_filename = project_name + ".zip"
    project_zip_path = os.path.join(project_path, project_zip_filename)

    with zipfile.ZipFile(project_zip_path, "w") as zf:
        for dirname, subdirs, files in os.walk(project_path):
            relpath = os.path.relpath(dirname, project_path)
            if relpath.startswith(".") and relpath != ".":
                continue

            for filename in files:
                file_path = os.path.join(dirname, filename)
                file_path_in_zip = os.path.join(relpath, filename)

                if filename == project_zip_filename:
                    continue

                print("Added: ", file_path_in_zip)

                zf.write(file_path, filename)

    print("Zipped: ", project_zip_filename)
    return zf.filename

def upload_to_bucket(file_path, bucket_name):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )

    filename = os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name, filename)
    print("Uploded: ", filename)

zip_path = zip_project(sys.argv[1])
upload_to_bucket(zip_path, 'bars-bucket')