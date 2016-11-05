from app import app
from flask import request, jsonify
from app.contact.forms import ContactForm
from werkzeug.datastructures import MultiDict

@app.route('/api/contact', methods=['POST'])
def send_mail():
    # TODO:for email support go to miguel book page 89
    data = request.get_json(force=True)
    form = ContactForm(MultiDict(mapping=data))
    if form.validate():
        username = data.get('user_name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        body = data.get('body')
        print data
        return jsonify({"success": "Votre message a ete recu, merci"}), 200
    return jsonify({"form_errors": form.errors}), 400
