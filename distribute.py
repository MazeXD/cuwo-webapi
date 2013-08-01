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


def move_file(src, dest):
    filename = os.path.basename(src)
    shutil.copyfile(src, "%s/%s" % (dest, filename))


def get_git_rev(folder, long_form=False):
    log_file = os.path.join(folder, '.git', 'logs', 'HEAD')
    if not os.path.isfile(log_file):
        return None
    line = None
    with open(log_file, 'rb') as f:
        line = f.readlines()[-1]
    rev = line.split(' ')[1]
    if long_form:
        return rev
    return rev[:7]


if __name__ == "__main__":
    filename = 'webapi'
    git_rev = get_git_rev('.')
    dist_name = filename
    if git_rev:
        dist_name += '-%s' % git_rev
    dist_folder = './dist'
    build_folder = './build'
    print 'Cleaning up'
    clean_up(build_folder)
    print 'Building Package:'
    build_package('%s/scripts' % build_folder, filename, True)
    print 'Moving Bootstrap script'
    move_file('webapi.py', '%s/scripts' % build_folder)
    print 'Packaging:'
    package(dist_folder, dist_name, True, '%s/scripts' % build_folder, 'config')
