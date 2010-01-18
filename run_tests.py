try:
    from d51.django.virtualenv.test_runner import run_tests
except ImportError:
    print "Please install d51.django.virtualenv.test_runner to run these tests"

def main():
    settings = {
        "INSTALLED_APPS": (
            "d51.django.apps.invites",
        ),
    }
    run_tests(settings, 'invites')

if __name__ == '__main__':
    main()
