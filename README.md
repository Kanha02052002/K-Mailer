
# K-Mailer

This project is a Flask-based email automation system that allows users to send emails in three different modes:
1. **Cold Email**: Sending personalized emails to a list of recipients from a CSV file.
2. **Bulk Email**: Sending bulk emails to multiple recipients.
3. **Template Email**: Sending email templates with HTML content to a list of recipients.




## Screenshots

![App Screenshot](https://github.com/Kanha02052002/K-Mailer/blob/main/K-Mailer%20home.png)

The application also generates a report of sent emails in CSV format, which can be downloaded after the emails are sent.

## Tech Stack
- **Backend**: Python 3, Flask
- **Email Service**: Gmail SMTP for sending emails
- **Frontend**: HTML, CSS, JavaScript (with Jinja templating)
- **Libraries**:
  - `Flask`: Web framework
  - `Flask-Mail`: Email handling
  - `pandas`: For processing CSV files
  - `os`: File and directory operations
  - `smtplib`, `email.mime`: For email sending with attachments
  - `csv`: For reading and writing CSV files

## Requirements

Before running this application, ensure you have the following installed:
- Python 3.10 
- Flask
- Flask-Mail
- pandas
- SMTP server access (Gmail recommended)

You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```
Make sure to set up your Gmail account and allow "Less Secure Apps" if necessary or use an "App Password" for enhanced security.

## Setup and Running the Application
Clone the repository:

```bash
git clone <repository_url>
cd <repository_name>
```
Set up your secret key:
```bash
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
```
Run the Flask app:

```bash
python app.py
```
Open a browser and navigate to http://127.0.0.1:5000/ to access the app.
