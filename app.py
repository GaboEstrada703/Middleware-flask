from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token de verificación para Meta
VERIFY_TOKEN = "c89b10e3f20a4fba92b3a77cf044c9a9"

# URL de webhook de Teams
TEAMS_WEBHOOK_URL = 'https://activastudiolegal.webhook.office.com/webhookb2/5e6c94e4-5e61-4ba9-93e3-1d9cf1fa36bf@9df9b718-99b2-41da-8a6c-a00abb51cfa4/IncomingWebhook/79a80563e26249459d87786c70548aca/b9bc5f66-2d0b-4a73-8aed-fe2c32200f8c/V2FNr-vijxsGutIP27_FINNKUpszSAEL7wZuO5DMFJdZ41'
WHATSAPP_API_URL = 'https://graph.facebook.com/v21.0/412094048659989/messages'
WHATSAPP_API_TOKEN = 'EAATqeZByp0JABOxcV0qj1omApuXUhgrH2mNNnFJnMOb6nJZA0gTkZCNQtjggSty3vkYGj5fPU76sRIK9Rv1pqUNZCHcL0M9V2UUtCQdZClvtv1N0kxy4p6ycDXym6aH41DfGwSnPoSTyCaynUBHrIwU1ABKhdUnSV6P7tVyi8t109ey9yq8pvZAVHh8G0jCTqL6LWu0uAXHZAOFHBws1kfDmYIG37sEzCM0ZCt4ZD'

# Ruta para la verificación inicial del webhook de WhatsApp
@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        # Verificación del token
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Verificación fallida", 403
    elif request.method == 'POST':
        # Procesa los mensajes entrantes después de la verificación
        data = request.get_json()
        print(f"Mensaje recibido: {data}")
        return "EVENT_RECEIVED", 200

# Ruta para recibir mensajes de WhatsApp y enviarlos a Teams
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook_handler():
    data = request.get_json()
    print(f"Datos recibidos de WhatsApp: {data}")

    message_content = data.get('message', 'Mensaje sin contenido')

    # Crear el payload para Teams
    payload = {
        "text": f"Mensaje de WhatsApp: {message_content}"
    }

    # Enviar el mensaje a Teams
    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Mensaje enviado a Teams con éxito")
        return jsonify({"status": "Mensaje enviado a Teams"}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error enviando a Teams: {e}")
        return jsonify({"error": "No se pudo enviar a Teams"}), 500

# Ruta para recibir respuestas desde Teams y enviarlas a WhatsApp
@app.route('/teams_response', methods=['POST'])
def teams_response():
    data = request.get_json()
    print(f"Datos recibidos de Teams: {data}")

    response_message = data.get('text', 'Respuesta sin contenido')

    # Enviar respuesta a WhatsApp
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "50612345678",  # Reemplaza con el número de destino en formato correcto
        "type": "text",
        "text": {
            "body": response_message
        }
    }
    print(f"Enviando respuesta a WhatsApp con headers: {headers}")
    print(f"Payload enviado a WhatsApp: {payload}")

    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        print("Respuesta enviada a WhatsApp con éxito")
        return jsonify({"status": "Respuesta enviada a WhatsApp"}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error enviando a WhatsApp: {e}")
        if e.response is not None:
            print(f"Respuesta de error de WhatsApp: {e.response.json()}")
        return jsonify({"error": "No se pudo enviar a WhatsApp"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Azure usa la IP '0.0.0.0' para permitir el acceso externo
