from subprocess import call

for [path, dirnames, filenames] in walk(dirname):
    for filename in filenames:
        call(["gpg", "-output " + filename.split(".gpg")[0] + " --decrypt " + filename])
