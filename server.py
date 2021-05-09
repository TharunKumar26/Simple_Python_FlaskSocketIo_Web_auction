from flask import Flask, render_template,url_for,redirect,session,request
from flask_socketio import SocketIO
import threading
import time
usercount=0
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
products=[{
    
    'id':'0',
    'expire':1010,
    'url':"http://www.villagecraftsmen.com/goodwin_blksquall.1.75tequila.jpg",
    'bids':[
    {'userid':1,'bid':70},
    {'userid':2,'bid':40},
    {'userid':1,'bid':20},
    ]
},

{
    
    'id':'1',
    'expire':1600,
    'url':'https://asset.swarovski.com/images/$size_1450/t_swa103/b_rgb:ffffff,c_scale,dpr_3.0,f_auto,w_500/5184204_png/attract-round-ring--white--rose-gold-tone-plated-swarovski-5184204.png',
    'bids':[
    {'userid':1,'bid':70,'name':'TK'},
    {'userid':2,'bid':40,'name':'TK'},
    {'userid':1,'bid':20,'name':'TK'},
    ]
},
{
    
    'id':'2',
    'expire':2600,
    'url':'https://i.pinimg.com/originals/d0/07/03/d007039f3c3d356449a2f3958017ef94.jpg',
    'bids':[
    {'userid':2,'bid':100,'name':'TK'},
    {'userid':1,'bid':40,'name':'varsha'},
    {'userid':1,'bid':20,'name':'TK'},
    ]
}

]

bids={}
user={}
username={}
email={}

users = [
    {'id':1,'username' :'tk'},
    {'id':2,'username':'teja'}
]


def Check():
    seconds = 0
    while  True:
        seconds = seconds +1
        time.sleep(1000)
        for n in products:
            n["expired"]-=1
            if n['expire'] <= 0 :
                socketio.emit('product_expired',{
                    id : n[id]
                })

#threading.Thread(target = check).start()


            



@app.route('/')
def sessions():
    if "user" in session:
        name = session['user']
        return render_template('web2.html',name = name, product = products)  
    else:
        return render_template('web1.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
@app.route('/product', methods=['GET'])
def product():
    if 'user' in session:

        id = request.args.get('id')
        print('id',id)
        for n in products:
            print(n)
            if str(n['id'])==str(id):
                return render_template('web3.html', name = session['user'], product = n, id=id , expire = n['expire'] )
                
        # product = products[int(id)]['bids']

        
    else:
        return render_template('web1.html')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    print(request.form['user'])
    userdata = {
        'id' : len(users)+1,
        'username' : request.form['user'], 
    }
    users.append(userdata)
    if request.method == 'POST':
        session['user'] = request.form['user']
    name = 'User'
    if 'user' in session:
        name = session['user']
    return render_template('web2.html',name = name)



@app.route('/Home', methods=['GET', 'POST'])
def Home():

   
    name = 'User'
    if 'user' in session:
        name = session['user']
    return render_template('web2.html',product=products,name=name)

@app.route('/Logout', methods=['GET', 'POST'])
def Logout():

   
    
    if 'user' in session:
        session.pop('user')
    return render_template('web1.html')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
@socketio.on('user login')
def handle_auction(result, methods=['GET', 'POST']):
    print('user bidding done for: ' + str(result))
    username[result["email"]]=result["username"]
    session["username"]=result["username"]
    return redirect(url_for("Home"))
    print(username[0])
    socketio.emit('home page', result, callback=messageReceived)

@socketio.on('user_bid')
def handle_bids(result, methods=['POST', 'GET']):
    session['id'] =  request.sid

    for n in range(len(user)):
        if user[n] != session['id']:
            socketio.emit('notification',{
            'product_id' :result['id'],
            'name' : session['user'],
            'bid' : int(result['bid_amount'])
    }, room = user[n])
    bid = int(result['bid_amount'])
    name = session['user']
    id = result['id']
    print(bid, products[id]['bids'][0]['bid'])
    if(bid <= int(products[id]['bids'][0]['bid'])):
        return socketio.emit('bid_placed',{'msg':request.sid})
    else:
    

        bid_data = {'userid': 1,
                    'bid':bid,
                    'name': name}

        products[id]['bids'].insert(0,bid_data)

        socketio.emit('bid_placed',{'msg':'bid place successfully'}, room = session['id'])
@socketio.on('product sold')
def handle_del(res):
    del products[int(res['id'])]
    print(res)

@socketio.on('connect')
def test_connect():
    global usercount
   
    print("Client connected: " + request.sid)

    # Prints None, even if authenticated
    # Link user ID with session ID
    user[usercount]= request.sid
    print(user)
    usercount += 1
if __name__ == '__main__':
    socketio.run(app, debug=True)