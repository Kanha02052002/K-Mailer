from flask import Flask, render_template, request, flash, redirect, url_for, send_file, session
from flask_mail import Mail, Message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import pandas as pd
import csv

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)

REPORT_FOLDER = "reports"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

def sanitize_filename(filename):
    filename = filename.replace(" ", "_")  
    return "".join(c for c in filename if c.isalnum() or c in (".", "_", "-")) 

def send_email_cold(sender_email, sender_password, recipient, receiver_name, subject, message, sender_name, attachment_path=None):
    try:
        app.config["MAIL_USERNAME"] = sender_email
        app.config["MAIL_PASSWORD"] = sender_password
        mail.init_app(app)

        formatted_message = f"Dear {receiver_name},\n\n{message}\n\nThank you,\n{sender_name}"
        msg = Message(subject, sender=sender_email, recipients=[recipient])
        msg.body = formatted_message

        if attachment_path:
            with app.open_resource(attachment_path) as attached_file:
                msg.attach(os.path.basename(attachment_path), "application/pdf", attached_file.read())

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return False

def send_email_bulk(sender_email, sender_password, recipient_email, sender_name, subject, message, attachment_path=None):
    try:
        app.config["MAIL_USERNAME"] = sender_email
        app.config["MAIL_PASSWORD"] = sender_password
        mail.init_app(app)

        formatted_message = f"{message}"
        msg = Message(subject, sender=sender_email, recipients=[recipient_email])
        msg.body = formatted_message

        if attachment_path:
            with app.open_resource(attachment_path) as attached_file:
                msg.attach(os.path.basename(attachment_path), "application/pdf", attached_file.read())

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False
    
def send_email_template(sender_email, app_password, recipient_emails, subject, html_message):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_message, "html"))

        msg["To"] = ", ".join(recipient_emails)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()

        return "Emails sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

def clear_uploads():
    for folder in [UPLOAD_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cold-mail", methods=["GET", "POST"])
def cold_mail():
    clear_uploads()
    if request.method == "POST":
        try:
            sender_name = request.form["name"]
            sender_email = request.form["sender_email"]
            sender_password = request.form["sender_password"]
            subject = request.form.get("subject", "No Subject")
            message = request.form["message"]
            file = request.files["file"]
            attachment = request.files["attachment"]
            csv_filename = sanitize_filename(file.filename)
            csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)
            file.save(csv_path)
            attachment_path = None
            attachment_name = "NONE"
            if attachment and attachment.filename:
                attachment_filename = sanitize_filename(attachment.filename)
                attachment_path = os.path.join(UPLOAD_FOLDER, attachment_filename)
                attachment.save(attachment_path)
                attachment_name = attachment_filename

            recipients_df = pd.read_csv(csv_path)
            results = []

            for _, row in recipients_df.iterrows():
                recipient_email = row["email"]
                receiver_name = row["name"]

                success = send_email_cold(sender_email, sender_password, recipient_email, receiver_name, subject, message, sender_name, attachment_path)
                status = "Success" if success else "Fail"
                results.append([sender_name, sender_email, receiver_name, recipient_email, subject, message, attachment_name, status])

            report_path = os.path.join(REPORT_FOLDER, "email_report.csv")
            pd.DataFrame(results, columns=["Sender Name", "Sender Email", "Receiver Name", "Receiver Email", "Subject", "Message", "Attachment", "Status"]).to_csv(report_path, index=False)

            session["email_sent"] = True
            flash("Emails sent successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for("cold_mail"))

    return render_template("cold-mail.html", email_sent=session.get("email_sent", False))

@app.route("/bulk-mail", methods=["GET", "POST"])
def bulk_mail():
    clear_uploads()
    
    if request.method == "POST":
        try:
            sender_name = request.form["name"]
            sender_email = request.form["sender_email"]
            sender_password = request.form["sender_password"]
            subject = request.form["subject"]
            message = request.form["message"]
            file = request.files["file"]
            attachment = request.files.get("attachment", None)

            csv_filename = sanitize_filename(file.filename)
            csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)
            file.save(csv_path)

            attachment_path = None
            attachment_name = "NONE"
            if attachment and attachment.filename:
                attachment_filename = sanitize_filename(attachment.filename)
                attachment_path = os.path.join(UPLOAD_FOLDER, attachment_filename)
                attachment.save(attachment_path)
                attachment_name = attachment_filename

            recipients_df = pd.read_csv(csv_path)
            if "email" not in recipients_df.columns:
                flash("CSV file must contain a column named 'email'", "danger")
                return redirect(url_for("bulk_mail"))

            results = []

            for _, row in recipients_df.iterrows():
                recipient_email = row["email"]
                
                success = send_email_bulk(sender_email, sender_password, recipient_email, sender_name, subject, message, attachment_path)
                status = "Success" if success else "Fail"
                results.append([sender_name, sender_email, recipient_email, subject, message, attachment_name, status])

            report_path = os.path.join(REPORT_FOLDER, "email_report.csv")
            pd.DataFrame(results, columns=["Sender Name", "Sender Email", "Receiver Email", "Subject", "Message", "Attachment", "Status"]).to_csv(report_path, index=False)

            session["email_sent"] = True
            flash("Emails sent successfully!", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for("bulk_mail"))

    return render_template("bulk-mail.html", email_sent=session.get("email_sent", False))

@app.route("/template-mail", methods=["GET", "POST"])
def send_email():
    result=""
    if request.method == "POST":
        sender_email = request.form["sender_email"]
        app_password = request.form["sender_password"]
        subject = request.form["subject"]
        html_message = request.form["message"]

        if "csv_file" in request.files:
            csv_file = request.files["csv_file"]
            recipient_emails = []

            try:
                csv_data = csv_file.read().decode("utf-8").splitlines()
                csv_reader = csv.DictReader(csv_data)
                for row in csv_reader:
                    recipient_emails.append(row["email"])
                
                result = send_email_template(sender_email, app_password, recipient_emails, subject, html_message)
                print(result)
            except Exception as e:
                result=f"Failed to process the CSV file: {str(e)}"
                print(result)
    return render_template("template.html", result=result)

@app.route("/download")
def download():
    report_path = os.path.join(REPORT_FOLDER, "email_report.csv")
    if not os.path.exists(report_path):
        flash("Error: Report not found!", "danger")
        return redirect(url_for("index"))
    return send_file(report_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
