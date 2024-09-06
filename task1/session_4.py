from flask import Flask, render_template, redirect, url_for


app = Flask(__name__)
students = [{"id":1, "name":"Ahmed"}, {"id":2, "name":"Mohamed"}, {"id":3, "name":"Youssef"}]

@app.route("/")
def home_page():
    # global students # for modification

    # return {"id": 1, "name":"Ahmed"}
    # return "<h1>Home Page</h1>"
    return render_template("index.html", students_data=students)

@app.route("/search/<int:id>") # search/1 => data in table of user that has id=1
def search(id):
    isFound = False
    targetStudent = None
    for student in students:
        if student['id'] == id:
            isFound = True
            targetStudent = student
    return render_template("search.html",isFound=isFound,targetStudent=targetStudent)




if __name__ == "__main__":  # Correct syntax
    app.run(debug=True, port=5000)
