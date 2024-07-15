import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from database import init_db, get_db, get_user, create_user, add_group, get_groups, add_task, get_tasks, update_task, \
    delete_task, get_group_by_id, Task, update_group

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
init_db()


def get_or_create_user(db, telegram_id):
    user = get_user(db, telegram_id)
    if not user:
        user = create_user(db, telegram_id)
    return user


@app.route('/add_group', methods=['POST'])
def add_group_route():
    data = request.json
    telegram_id = str(data['telegram_id'])
    group_name = data['group_name']

    db = next(get_db())
    user = get_or_create_user(db, telegram_id)
    group = add_group(db, group_name, user.id)
    return jsonify({'group_id': group.id, 'group_name': group.name})


@app.route('/update_group', methods=['POST'])
def update_group_route():
    data = request.json
    group_id = data['group_id']
    group_name = data['group_name']

    db = next(get_db())
    group = update_group(db, group_id, group_name)
    return jsonify({'group_id': group.id, 'group_name': group.name})

@app.route('/delete_group', methods=['POST'])
def delete_group_route():
    data = request.json
    group_id = data['group_id']

    db = next(get_db())
    group = get_group_by_id(db, group_id)
    if group:
        db.session.delete(group)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/get_groups', methods=['POST'])
def get_groups_route():
    data = request.json
    telegram_id = str(data['telegram_id'])

    db = next(get_db())
    user = get_or_create_user(db, telegram_id)
    groups = get_groups(db, user.id)
    if groups is None or len(groups) == 0:
        add_group(db, "Новая группа", user.id)
    groups = get_groups(db, user.id)
    return jsonify({'groups': [{'id': group.id, 'name': group.name} for group in groups]})


@app.route('/add_task', methods=['POST'])
def add_task_route():
    data = request.json
    group_id = data['group_id']
    task_text = data['task']
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    custom_status = data.get('custom_status')

    if start_time:
        start_time = datetime.fromisoformat(start_time)
    else:
        start_time = datetime.now()
    if end_time:
        end_time = datetime.fromisoformat(end_time)
    if start_time < datetime.now():
        raise ValueError('Start time must be in the future')
    db = next(get_db())
    task = add_task(db, task_text, group_id, start_time, end_time, custom_status)
    return jsonify({'task': task.task, 'done': task.done, 'start_time': task.start_time, 'end_time': task.end_time,
                    'custom_status': task.custom_status})


@app.route('/get_tasks', methods=['POST'])
def get_tasks_route():
    data = request.json
    group_id = data['group_id']

    db = next(get_db())
    group = get_group_by_id(db, group_id)
    tasks = get_tasks(db, group_id)
    if tasks is None or len(tasks) == 0:
        add_task(db, "Новая задача", group_id)
        tasks = get_tasks(db, group_id)
    json_tasks = [{'id': task.id, 'task': task.task, 'done': task.done,
                   'start_time': task.start_time, 'end_time': task.end_time,
                   'custom_status': task.custom_status, 'group': group.name
                   } for task, group in tasks]
    return jsonify({'tasks': json_tasks, 'group': {'id': group.id, 'name': group.name}})


@app.route('/update_task', methods=['POST'])
def update_task_route():
    data = request.json
    task_id = data['task_id']
    done = data['done']
    group_id = data['group_id']

    db = next(get_db())
    task = update_task(db, task_id, done, group_id)
    return jsonify({'task': task.task, 'done': task.done})


@app.route('/delete_task', methods=['POST'])
def delete_task_route():
    data = request.json
    task_id = data['task_id']
    group_id = data['group_id']

    db = next(get_db())
    delete_task(db, task_id, group_id)
    return jsonify({'status': 'Task deleted'})


@app.route('/tasks_due', methods=['GET'])
def tasks_due():
    db = next(get_db())
    tasks = Task.get_due_tasks(db)
    if len(tasks) is None or len(tasks) == 0:
        return jsonify({})
    tasks_due = [
        {
            'user_id': task.main.user.telegram_id,
            'description': task.task
        }
        for task in tasks
    ]
    return jsonify(tasks_due)


@app.route('/update_task', methods=['POST'])
def update_task_status():
    data = request.get_json()
    task_id = data.get('task_id')
    db = next(get_db())
    task = update_task(
        db, task_id,
        data.get('done'),
        data.get('start_time'),
        data.get('end_time'),
        data.get('custom_status'),
    )
    if task:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure', 'message': 'Task not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
