from fabric.api import *
import os

def init():
    if not os.path.exists("./downloads"):
        local("mkdir ./downloads")
    local("python bootstrap.py")
    local("bin/buildout")

def setup_tests():
    if os.path.exists("./project-for-testing"):
        local("mv ./project-for-testing ./project")

def teardown_tests():
    local("mv ./project ./project-for-testing")

def test():
    setup_tests()
    local("bin/django test invites")
    teardown_tests()
