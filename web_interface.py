from flask import Flask, request, render_template

# Setup Flask
web = Flask(__name__)

saved = ''

# Path to index page
@web.route('/', methods=['GET', 'POST'])
def index():
    global saved
    content = '\n'
    if request.method == 'POST':
        print(request)
        for k in request.form:
            content += k
            content += request.form[k]
            content += '\n'
        saved = content
        print(content)
    elif request.method == 'GET':
        print(request)
        print(request.args)
        print(dir(request))
    # ~ print(state)
    # ~ print(code)
        
    return 'Hello?' + saved
    #return render_template('./index.html')

# Run when called
if __name__ == '__main__':
    web.run(debug=False, host='0.0.0.0', port=6500)
