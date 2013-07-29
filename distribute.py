import os
import shutil
import zipfile


def clean_up(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)


def build_package(folder, name, print_files=False):
    if not os.path.exists(folder):
        os.makedirs(folder)
    f = zipfile.PyZipFile('%s/%s.zip' % (folder, name), 'w')
    try:
        f.writepy(name)
    finally:
        f.close()
    if print_files:
        for filename in f.namelist():
            print '  %s' % filename


def package(folder, name, print_files=False, *includes):
    if not os.path.exists(folder):
        os.makedirs(folder)
    f = zipfile.ZipFile('%s/%s.zip' % (folder, name), 'w')
    try:
        for include in includes:
            for root, _, files in os.walk(include):
                for file in files:
                    path = os.path.join(root, file)
                    archive_path = os.path.join(os.path.basename(root), file)
                    f.write(path, archive_path)
    finally:
        f.close()
    if print_files:
        for filename in f.namelist():
            print '  %s' % filename


if __name__ == "__main__":
    filename = 'webapi'
    dist_folder = './dist'
    build_folder = './build'
    print 'Cleaning up'
    clean_up(build_folder)
    print 'Building Package:'
    build_package('%s/scripts' % build_folder, filename, True)
    print 'Packaging:'
    package(dist_folder, filename, True, '%s/scripts' % build_folder, 'config')
