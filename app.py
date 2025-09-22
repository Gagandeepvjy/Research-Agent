from flask import Flask, render_template, request, redirect, url_for, flash
import database
from agent_tool import generate_report

app = Flask(__name__)
app.secret_key = 'supersecretkey'

database.init_db()

@app.route('/')
def index():
    reports = database.get_all_reports()
    return render_template('index.html', reports=reports)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        query = request.form['query']
        if query:
            report, error = generate_report(query)
            if report:
                database.save_report(report['query'], report['summary'], report['key_points'], report['links'])
                flash('Report generated and saved successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(error, 'error')
        else:
            flash('Please enter a query.', 'error')
    return render_template('generate.html')

@app.route('/report/<int:report_id>')
def view_report(report_id):
    report = database.get_report_by_id(report_id)
    if report:
        return render_template('report.html', report=report)
    else:
        flash('Report not found.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
