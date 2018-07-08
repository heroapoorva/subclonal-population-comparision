import subprocess
import yaml
import json
from flask import (
    Flask, 
    render_template,
    request,
    redirect,
    url_for,
    Response
)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        yml = yaml.safe_load(request.data)
        with open("./yaml/gui_config.yaml", 'w') as o:
            yaml.dump(yml, o, allow_unicode=True)
        return "/running"
    else:
        return render_template("index.html")

@app.route("/running")
def running():
    return render_template("running.html")

@app.route("/logging")
def logging():
    def inner():
        cmd = "python main.py -c yaml/gui_config.yaml"
        with open("./yaml/gui_config.yaml", "r") as f:
            doc = yaml.safe_load(f)
        print(doc["use_intermediate"])
        print(doc["use_classified"])
        ccf_alg = doc["ccf_algorithm"]
        if doc["use_intermediate"] == True:
            cmd += " -i ../data/" + ccf_alg + "_500_intermediates/" + ccf_alg + "_500_intermediates"
        if doc["use_classified"] == True:
            cmd += " -a ../data/" + ccf_alg + "_500_classified_data.tsv/" + ccf_alg + "_500_classified_data.tsv"
        print(cmd)
        proc = subprocess.Popen(
            [cmd],
            shell=True,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        for line in iter(proc.stdout.readline,""):
            yield line.rstrip() + '\n'
        
    return Response(inner(), mimetype="text/plain")

@app.route("/results/")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")
