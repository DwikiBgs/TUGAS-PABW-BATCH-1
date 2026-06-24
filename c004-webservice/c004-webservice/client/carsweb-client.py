from flask import Flask, render_template, request, redirect, url_for
import json, requests

app = Flask(__name__)

global appType 

appType = 'Web Service'

@app.route('/')
def index():
    return render_template('index.html', appType=appType)

@app.route('/createcar')
def createcar():
    return render_template('createcar.html', appType=appType)

@app.route('/createcarsave',methods=['GET','POST'])
def createcarsave():
    fName = request.form['carName']
    fBrand = request.form['carBrand']
    fModel = request.form['carModel']
    fPrice = request.form['carPrice']

    datacar = {
        "carname" : fName,
        "carbrand" : fBrand, 
        "carmodel" : fModel,
        "carprice" : fPrice
    }
    
    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5012/cars/"
    
    headers = {'Content-Type':'application/json', 'Accept':'text/plain'}

    kirimdata = requests.post(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for('readcar'))


@app.route('/readcar')
def readcar():
    alamatserver = "http://localhost:5012/cars"
    datas = requests.get(alamatserver)

    rows = json.loads(datas.text)

    return render_template('readcar.html', rows=rows, appType=appType)

@app.route('/updatecar')
def updatecar():
    return render_template('updatecar.html', appType=appType)

@app.route('/updatecarsave', methods=['POST'])
def updatecarsave():
    fId = request.form.get('id')
    fName = request.form.get('carName')
    
    if fId and fName:
        datacar = {"id": fId, "carname": fName}
        # Mengirim request PUT ke server untuk update data
        requests.put("http://localhost:5012/cars", json=datacar)
        
    return redirect(url_for('readcar'))

@app.route('/deletecar')
def deletecar():
    return render_template('deletecar.html', appType=appType)

@app.route('/deletecarsave', methods=['GET','POST'])
def deletecarsave():
    fName = request.form['carName']

    datacar = {
        "carname" : fName
    }
    
    datacar_json = json.dumps(datacar)

    alamatserver = "http://localhost:5012/cars/"
    
    headers = {'Content-Type':'application/json', 'Accept':'text/plain'}

    kirimdata = requests.delete(alamatserver, data=datacar_json, headers=headers)

    return redirect(url_for('readcar'))

@app.route('/searchcar', methods=['GET'])
def searchcar():
    fName = request.args.get('keyword') 
    if fName:
        # Kirim query parameter ke server via GET /cars?keyword=nama_mobil
        response = requests.get("http://localhost:5012/cars", params={'keyword': fName})
        hasil_pencarian = response.json()
    else:
        hasil_pencarian = []
    return render_template('searchcar.html', cars=hasil_pencarian, keyword=fName)

if __name__ == '__main__':
    
    app.run(
        host = '0.0.0.0',
        debug = 'True',
        port=5011
        )