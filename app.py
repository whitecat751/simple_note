from flask import Flask, current_app
from flask import request, g, render_template, redirect, url_for
from datetime import datetime
import redis
import json


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = redis.StrictRedis(host='redis', db=0, socket_timeout=6)
    return g.redis

app = Flask(__name__)
with app.app_context():
    redis = get_redis()

def get_msgs():
    pass


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    if request.form.get("History") == "History":
        history_msgs = []

        for idx in redis.lrange('history', 0, 1):
            msg = redis.hgetall(f"msg_{str(idx, 'utf-8')}")
            history_msgs.append([list(map(lambda x: str(x, 'utf-8'), elm)) for elm in msg.items()][0])
        return render_template("history.html", history_msgs=history_msgs) 
    return render_template("index.html")

@app.route('/post_msg', methods=['GET', 'POST'])
def post_msg():
    if request.form.get("Submit") == "Submit":
        msg = request.form['text']
        data = {datetime.now().strftime('%d.%m.%y %H.%M.%S'): msg}
        indx = str(redis.incr('id'))
        idx = "msg_" + indx
        redis.hmset(idx, data)
        redis.lpush('history', indx)

    elif request.form.get("Return") == "Return":
        return redirect( url_for('index'))
    return  render_template("/post_msg.html")

@app.route('/history')
def history():
    if request.form.get("Return") == "Return":
        return redirect( url_for('index'))
    
    return render_template("/history.html")

if __name__ == '__main__':
     app.run(host="0.0.0.0")
