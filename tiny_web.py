from bottle import run, route


@route('/')
def index():
    return '<h1> Index Page </h1>'


if __name__ == '__main__':
    run()
