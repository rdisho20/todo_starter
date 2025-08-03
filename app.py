from uuid import uuid4

from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.exceptions import NotFound

from todos.utils import (
    error_for_list_title,
    error_for_todo,
    find_list_by_id,
    find_todo_by_id,
    mark_all_completed
)

app = Flask(__name__)
app.secret_key='secret1'

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('get_lists'))

@app.route("/lists")
def get_lists():
    lists = session['lists']
    return render_template("lists.html", lists=lists)

@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form["list_title"].strip()

    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=title)

    session['lists'].append({
        'id': str(uuid4()),
        'title': title,
        'todos': [],
    })

    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route("/lists/new")
def add_todo_list():
    return render_template("new_list.html")

@app.route("/lists/<list_id>")
def show_list(list_id):
    lst = find_list_by_id(list_id, session['lists'])

    if not lst:
        raise NotFound(description="List not found")

    return render_template('list.html', lst=lst)

@app.route("/lists/<list_id>", methods=["POST"])
def create_todo(list_id):
    todo_title = request.form["todo"].strip()
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise NotFound(description="List not found")

    error = error_for_todo(todo_title)
    if error:
        flash(error, "error")
        return render_template('list.html', lst=lst)
    
    lst['todos'].append({
        'id': str(uuid4()),
        'title': todo_title,
        'completed': False,
    })

    flash("The todo has been created.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=["POST"])
def update_todo_status(list_id, todo_id):
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise NotFound(description="List not found")

    todo = find_todo_by_id(todo_id, lst['todos'])
    if not todo:
        raise NotFound(description="Todo not found")
    
    todo['completed'] = (request.form['completed'] == 'True') # automatically converts to boolean value after evaluation
    flash(f"Todo '{todo['title']}' has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id)) # don't need todo_id because handled w/ temp var in Jinja2 template

@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
def delete_todo(list_id, todo_id):
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise NotFound(description="List not found")

    todo = find_todo_by_id(todo_id, lst['todos'])
    if not todo:
        raise NotFound(description="Todo not found")
    
    '''
    find todo by id, then determine its index position in lst['todos']
    remove the todo at that index position, printing title in success message
    '''
    todo_index = lst['todos'].index(todo)
    deleted_todo = lst['todos'].pop(todo_index)
    flash(f"Todo '{deleted_todo['title']}' has been DELETED.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/complete_all", methods=["POST"])
def complete_all_todos(list_id):
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise NotFound(description="List not found")
    
    mark_all_completed(lst)
    
    flash(f"All Todos have been marked COMPLETED.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)