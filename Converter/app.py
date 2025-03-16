from flask import Flask, request, render_template, jsonify
import subprocess
import os

app = Flask(__name__)

# Directory to store generated SiGML files
SIGML_DIR = "sigml"

# Ensure the SiGML directory exists
os.makedirs(SIGML_DIR, exist_ok=True)

# Generate SiGML file from HamNoSys input
def generate_sigml(word, hamnosys):
    try:
        sigml_path = os.path.join(SIGML_DIR, f"{word}.sigml")
        
        # Call the HamNoSys2SiGML script using subprocess
        command = ["python", "HamNoSys2SiGML.py", hamnosys]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Error generating SiGML: {result.stderr}")

        # Remove the first line if it starts with "<?xml"
        sigml_content = result.stdout
        if sigml_content.startswith("<?xml"):
            sigml_content = "\n".join(sigml_content.split("\n")[1:])

        # Save the processed output to the SiGML file
        with open(sigml_path, "w") as f:
            f.write(sigml_content)

        return sigml_path, sigml_content
    except Exception as e:
        print(f"Error generating SiGML: {e}")
        return None, str(e)


# Home route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# API to generate SiGML
@app.route('/generate', methods=['POST'])
def generate():
    try:
        word = request.form.get("word")
        hamnosys = request.form.get("hamnosys")

        if not word or not hamnosys:
            return jsonify({"error": "Both word and HamNoSys are required"}), 400

        sigml_path, sigml_content = generate_sigml(word, hamnosys)
        if not sigml_path:
            return jsonify({"error": "Failed to generate SiGML"}), 500

        print("Generated SiGML Content:", sigml_content)
        return render_template("result.html", word=word, sigml_content=sigml_content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

