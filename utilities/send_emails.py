import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def main():
    # names, emails = get_contacts('mycontacts.txt') # read contacts
    # message_template = read_template('message.txt')
    smtp_server = 'mail.help2go.ch'
    smtp_port = 465 #465
    smtp_user = 'mailhandler@psytex.ch'
    smtp_password = 'PaPaLo$99'
    smtp_encryption = 'ssl'
    names = ['robert'] 
    emails = ['robert@redcor.ch'] 
    message_template = Template('Hallo Velo')


    # set up the SMTP server
    server = smtplib.SMTP(host=smtp_server, port=smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        print(message)

        # setup the parameters of the message
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject']="This is a TEST"
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
        
        # send the message via the server set up earlier.
        server.sendmail(smtp_user, email, msg.as_string())
        del msg
        
    # Terminate the SMTP session and close the connection
    server.quit()
    
if __name__ == '__main__':
    main()