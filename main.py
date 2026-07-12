from flask import Flask, request, jsonify
from linkedin_agent import graph

app = Flask(__name__)

@app.route("/formmodel", methods=["POST"])
def fetchUser():
    try:
        file = request.files.get("user_file")

        if file is None:
            return jsonify({"error": "No file uploaded"}), 400

        state = {
            "file_path": file.stream,
            "input_type": "file"
        }

        result = graph.invoke(state)

        return jsonify({
            "headline": result.get("headline"),
            "about": result.get("about"),
            "skills": result.get("skills"),
            "keywords": result.get("keywords"),
            "experience": result.get("experience"),
            "headline_review": result.get("headline_review"),
            "about_review": result.get("about_review"),
            "branding_review": result.get("branding_review"),
            "networking_review": result.get("networking_review"),
            "ats_score": result.get("ats_score"),
            "final_score": result.get("final_score")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/textmodel", methods=["POST"])
def fetchUsertext():
    try:
        if request.is_json:
            input_text = request.json.get("input_text")
        else:
            input_text = request.form.get("input_text")

        if not data or "input_text" not in data:
            return jsonify({"error": "No text uploaded"}), 400

        state = {
            "input_text": data["input_text"],
            "input_type": "text"
        }

        result = graph.invoke(state)

        return jsonify({
            "headline": result.get("headline"),
            "about": result.get("about"),
            "skills": result.get("skills"),
            "keywords": result.get("keywords"),
            "experience": result.get("experience"),
            "headline_review": result.get("headline_review"),
            "about_review": result.get("about_review"),
            "branding_review": result.get("branding_review"),
            "networking_review": result.get("networking_review"),
            "ats_score": result.get("ats_score"),
            "final_score": result.get("final_score")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
